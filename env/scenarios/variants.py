"""
Scenario variant registry — randomized bugs so every run is different.
Each task has 3 variants. The engine picks one randomly per reset.
"""
from __future__ import annotations
from typing import Dict, List, Tuple

# ── Memory Leak variants ──────────────────────────────────────────────────────
MEMORY_LEAK_VARIANTS: List[Dict] = [
    {
        "id": "ml_v1",
        "label": "Unbounded User Cache",
        "buggy_file": "api/users.js",
        "buggy_code": """\
// api/users.js — User lookup service
const express = require('express');
const router = express.Router();
const userCache = {};  // BUG: no eviction
router.get('/user/:id', async (req, res) => {
  const { id } = req.params;
  if (!userCache[id]) {
    userCache[id] = { id, name: `User_${id}`,
      metadata: Buffer.alloc(1024 * 50).toString('base64'), fetchedAt: Date.now() };
  }
  res.json(userCache[id]);
});
module.exports = router;
""",
        "tests": [
            ("Cache has eviction", lambda c: "delete" in c or "Map" in c or "evict" in c.lower()),
            ("No unbounded object", lambda c: "userCache = {}" not in c),
            ("TTL or size limit", lambda c: "TTL" in c or "MAX_CACHE" in c or "size" in c.lower()),
            ("Returns user data", lambda c: "res.json" in c),
        ],
        "root_cause": "api/users.js: userCache = {} has no eviction policy",
        "optimal_fix": "Replace with Map + TTL eviction + MAX_CACHE_SIZE limit",
        "hint": "The memory leak is in api/users.js. The global `userCache = {}` has no eviction. Add a Map with TTL and size limit.",
        "logs_extra": ["[2026-04-05T10:10:00Z] ERROR heap used: 487MB / 512MB — userCache has 9800 entries"],
    },
    {
        "id": "ml_v2",
        "label": "Event Listener Accumulation",
        "buggy_file": "services/eventBus.js",
        "buggy_code": """\
// services/eventBus.js — Event bus service
const EventEmitter = require('events');
const bus = new EventEmitter();
bus.setMaxListeners(0); // BUG: unlimited listeners — never removed

function subscribe(event, handler) {
  bus.on(event, handler); // BUG: listeners added but never removed
}

function publish(event, data) {
  bus.emit(event, data);
}

module.exports = { subscribe, publish };
""",
        "tests": [
            ("Listener cleanup", lambda c: "removeListener" in c or "off(" in c or "once(" in c),
            ("Max listeners set", lambda c: "setMaxListeners(0)" not in c),
            ("Publish still works", lambda c: "emit" in c),
            ("Subscribe still works", lambda c: "on(" in c or "once(" in c),
        ],
        "root_cause": "services/eventBus.js: listeners added with bus.on() but never removed",
        "optimal_fix": "Use bus.once() for one-time handlers, or call removeListener() on cleanup",
        "hint": "The leak is in services/eventBus.js. Listeners are added with bus.on() but never removed. Use bus.once() or call removeListener() on cleanup.",
        "logs_extra": ["[2026-04-05T10:10:00Z] WARN EventEmitter: possible memory leak — 9800 listeners added to 'data' event"],
    },
    {
        "id": "ml_v3",
        "label": "Unclosed Database Connections",
        "buggy_file": "db/queries.js",
        "buggy_code": """\
// db/queries.js — Database query helper
const { Pool } = require('pg');
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

async function runQuery(sql, params) {
  const client = await pool.connect(); // BUG: client never released
  try {
    const result = await client.query(sql, params);
    return result.rows;
  } catch (err) {
    throw err;
    // BUG: missing finally { client.release() }
  }
}

module.exports = { runQuery };
""",
        "tests": [
            ("Client released in finally", lambda c: "finally" in c and "release" in c),
            ("Error still thrown", lambda c: "throw" in c),
            ("Query still runs", lambda c: "query" in c),
            ("No connection leak", lambda c: "client.release()" in c),
        ],
        "root_cause": "db/queries.js: pool.connect() called but client.release() never called in finally block",
        "optimal_fix": "Add finally { client.release() } after the try/catch block",
        "hint": "The leak is in db/queries.js. pool.connect() acquires a client but client.release() is never called. Add a finally block.",
        "logs_extra": ["[2026-04-05T10:10:00Z] ERROR pg: connection pool exhausted — 100/100 connections in use"],
    },
]

# ── DB Deadlock variants ──────────────────────────────────────────────────────
DB_DEADLOCK_VARIANTS: List[Dict] = [
    {
        "id": "dd_v1",
        "label": "Inconsistent Lock Order",
        "buggy_file": "services/transfer.js",
        "buggy_code": """\
// services/transfer.js — Fund transfer
const db = require('../db');
async function transferFunds(fromId, toId, amount) {
  const client = await db.pool.connect();
  try {
    await client.query('BEGIN');
    const from = await client.query('SELECT balance FROM accounts WHERE id=$1 FOR UPDATE',[fromId]);
    const to = await client.query('SELECT balance FROM accounts WHERE id=$1 FOR UPDATE',[toId]);
    if (from.rows[0].balance < amount) throw new Error('Insufficient funds');
    await client.query('UPDATE accounts SET balance=balance-$1 WHERE id=$2',[amount,fromId]);
    await client.query('UPDATE accounts SET balance=balance+$1 WHERE id=$2',[amount,toId]);
    await client.query('COMMIT');
    return { success: true };
  } catch (err) { await client.query('ROLLBACK'); throw err; }
  finally { client.release(); }
}
module.exports = { transferFunds };
""",
        "tests": [
            ("Consistent lock order", lambda c: ("firstId" in c and "secondId" in c) or "Math.min" in c or "ascending" in c.lower()),
            ("ROLLBACK present", lambda c: "ROLLBACK" in c),
            ("COMMIT present", lambda c: "COMMIT" in c),
            ("Balance check", lambda c: "balance" in c and "amount" in c),
        ],
        "root_cause": "services/transfer.js: locks acquired in caller order — concurrent transfers deadlock",
        "optimal_fix": "Always lock accounts in ascending ID order: const [first,second] = fromId < toId ? [fromId,toId] : [toId,fromId]",
        "hint": "Deadlock in services/transfer.js. Lock accounts in ascending ID order to prevent circular waits.",
        "logs_extra": ["[2026-04-05T14:02:00Z] ERROR PostgreSQL deadlock detected: process 1234 waits for ShareLock on transaction 5678"],
    },
    {
        "id": "dd_v2",
        "label": "Missing Transaction Isolation",
        "buggy_file": "services/inventory.js",
        "buggy_code": """\
// services/inventory.js — Inventory reservation
const db = require('../db');
async function reserveItem(itemId, quantity, userId) {
  // BUG: No transaction — race condition between check and update
  const item = await db.pool.query('SELECT stock FROM inventory WHERE id=$1',[itemId]);
  if (item.rows[0].stock < quantity) throw new Error('Out of stock');
  // Another request can run here and also see sufficient stock!
  await db.pool.query('UPDATE inventory SET stock=stock-$1 WHERE id=$2',[quantity,itemId]);
  await db.pool.query('INSERT INTO reservations(item_id,user_id,qty) VALUES($1,$2,$3)',[itemId,userId,quantity]);
  return { reserved: true };
}
module.exports = { reserveItem };
""",
        "tests": [
            ("Uses transaction", lambda c: "BEGIN" in c or "transaction" in c.lower()),
            ("FOR UPDATE lock", lambda c: "FOR UPDATE" in c or "SERIALIZABLE" in c),
            ("Stock check inside tx", lambda c: "BEGIN" in c and "stock" in c),
            ("Rollback on error", lambda c: "ROLLBACK" in c or "catch" in c),
        ],
        "root_cause": "services/inventory.js: check-then-act without transaction — classic TOCTOU race condition",
        "optimal_fix": "Wrap in BEGIN/COMMIT with SELECT FOR UPDATE to lock the row during check",
        "hint": "Race condition in services/inventory.js. The stock check and update are not in a transaction. Use BEGIN + SELECT FOR UPDATE + COMMIT.",
        "logs_extra": ["[2026-04-05T14:02:00Z] ERROR inventory: stock went negative — concurrent reservations oversold item #4821"],
    },
    {
        "id": "dd_v3",
        "label": "N+1 Query Deadlock",
        "buggy_file": "api/orders.js",
        "buggy_code": """\
// api/orders.js — Order processing
const db = require('../db');
async function processOrders(orderIds) {
  const results = [];
  for (const id of orderIds) {
    // BUG: Each iteration opens a transaction and locks rows
    // Concurrent calls with overlapping orderIds cause deadlock
    const client = await db.pool.connect();
    await client.query('BEGIN');
    const order = await client.query('SELECT * FROM orders WHERE id=$1 FOR UPDATE',[id]);
    await client.query('UPDATE orders SET status=$1 WHERE id=$2',['processing',id]);
    await client.query('COMMIT');
    client.release();
    results.push(order.rows[0]);
  }
  return results;
}
module.exports = { processOrders };
""",
        "tests": [
            ("Single transaction for batch", lambda c: c.count("BEGIN") <= 1 or "Promise.all" in c),
            ("No per-item transaction", lambda c: "for" not in c or "BEGIN" not in c.split("for")[1] if "for" in c else True),
            ("Still processes orders", lambda c: "UPDATE orders" in c),
            ("Releases connection", lambda c: "release()" in c),
        ],
        "root_cause": "api/orders.js: per-item transactions in a loop — concurrent calls with shared order IDs deadlock",
        "optimal_fix": "Process all orders in a single transaction, or use Promise.all with proper ordering",
        "hint": "Deadlock in api/orders.js. Each loop iteration opens a separate transaction. Batch all updates in one transaction.",
        "logs_extra": ["[2026-04-05T14:02:00Z] ERROR deadlock detected in processOrders — overlapping order IDs locked by concurrent requests"],
    },
]

# ── Cascade Failure variants ──────────────────────────────────────────────────
CASCADE_VARIANTS: List[Dict] = [
    {
        "id": "cf_v1",
        "label": "Redis Timeout Cascade",
        "buggy_file": "service-a/cache.js",
        "buggy_code": """\
// service-a/cache.js — Session cache
const redis = require('redis');
const client = redis.createClient({ url: process.env.REDIS_URL });
// BUG: No timeout, no circuit breaker
client.on('error', (err) => console.error('Redis error:', err));
client.connect();
async function getSession(sessionId) {
  const data = await client.get(`session:${sessionId}`); // hangs if Redis slow
  return data ? JSON.parse(data) : null;
}
async function setSession(sessionId, data, ttl = 3600) {
  await client.setEx(`session:${sessionId}`, ttl, JSON.stringify(data));
}
module.exports = { getSession, setSession };
""",
        "tests": [
            ("Timeout configured", lambda c: "connectTimeout" in c or "commandTimeout" in c or "timeout" in c.lower()),
            ("Circuit breaker", lambda c: "circuit" in c.lower() or "circuitOpen" in c),
            ("Graceful degradation", lambda c: "return null" in c or "catch" in c),
            ("Error handler", lambda c: "catch" in c or "error" in c.lower()),
        ],
        "root_cause": "service-a/cache.js: Redis client has no timeout — blocks event loop when Redis is slow",
        "optimal_fix": "Add socket.connectTimeout, Promise.race timeout, and circuit breaker pattern",
        "hint": "Root cause is service-a/cache.js. Redis client has no timeout. Service B/C errors are symptoms. Add connectTimeout and circuit breaker.",
        "logs_extra": ["[2026-04-05T16:04:55Z] ERROR service-a: Redis ETIMEDOUT — event loop blocked 4200ms"],
    },
    {
        "id": "cf_v2",
        "label": "HTTP Retry Storm",
        "buggy_file": "service-b/client.js",
        "buggy_code": """\
// service-b/client.js — HTTP client for Service A
const axios = require('axios');
// BUG: Aggressive retry with no backoff — amplifies failures
async function callServiceA(endpoint, data) {
  let lastError;
  for (let i = 0; i < 10; i++) { // BUG: 10 retries with no delay
    try {
      return await axios.post(`http://service-a${endpoint}`, data, { timeout: 30000 });
    } catch (err) {
      lastError = err;
      // BUG: No backoff — immediately retries, flooding Service A
    }
  }
  throw lastError;
}
module.exports = { callServiceA };
""",
        "tests": [
            ("Exponential backoff", lambda c: "backoff" in c.lower() or "Math.pow" in c or "delay" in c.lower() or "sleep" in c.lower()),
            ("Max retries reduced", lambda c: "< 3" in c or "< 4" in c or "retries = 3" in c or "maxRetries" in c),
            ("Jitter added", lambda c: "Math.random" in c or "jitter" in c.lower() or "backoff" in c.lower()),
            ("Still retries", lambda c: "retry" in c.lower() or "for" in c),
        ],
        "root_cause": "service-b/client.js: 10 immediate retries with no backoff — floods Service A during degradation",
        "optimal_fix": "Implement exponential backoff with jitter: delay = Math.min(1000 * 2^attempt + random, 30000)",
        "hint": "The retry storm is in service-b/client.js. 10 retries with no delay floods Service A. Add exponential backoff with jitter.",
        "logs_extra": ["[2026-04-05T16:05:00Z] ERROR service-b: 847 requests/sec to service-a — retry storm detected"],
    },
    {
        "id": "cf_v3",
        "label": "Connection Pool Exhaustion",
        "buggy_file": "service-a/db.js",
        "buggy_code": """\
// service-a/db.js — Database connection pool
const { Pool } = require('pg');
// BUG: Pool size too large — exhausts DB connections under load
// BUG: No connection timeout — requests queue forever
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 100,          // BUG: 100 connections per instance × 10 instances = 1000 > DB limit
  idleTimeoutMillis: 0, // BUG: connections never released when idle
  connectionTimeoutMillis: 0, // BUG: waits forever for a connection
});
module.exports = { pool };
""",
        "tests": [
            ("Pool size reduced", lambda c: "max: 10" in c or "max: 5" in c or "max: 20" in c or ("max:" in c and "100" not in c.split("max:")[1][:5] if "max:" in c else False)),
            ("Idle timeout set", lambda c: "idleTimeoutMillis" in c and "0," not in c.split("idleTimeoutMillis")[1][:5] if "idleTimeoutMillis" in c else False),
            ("Connection timeout set", lambda c: "connectionTimeoutMillis" in c and "0," not in c.split("connectionTimeoutMillis")[1][:5] if "connectionTimeoutMillis" in c else False),
            ("Pool still created", lambda c: "new Pool" in c),
        ],
        "root_cause": "service-a/db.js: pool max=100 per instance exhausts DB connection limit; no timeouts",
        "optimal_fix": "Set max: 10, idleTimeoutMillis: 30000, connectionTimeoutMillis: 5000",
        "hint": "The cascade starts in service-a/db.js. Pool max=100 × 10 instances = 1000 connections exceeds DB limit. Reduce max and add timeouts.",
        "logs_extra": ["[2026-04-05T16:05:00Z] ERROR service-a: remaining connection slots reserved for non-replication superuser connections"],
    },
]

ALL_VARIANTS = {
    "memory_leak": MEMORY_LEAK_VARIANTS,
    "db_deadlock": DB_DEADLOCK_VARIANTS,
    "cascade_failure": CASCADE_VARIANTS,
}
