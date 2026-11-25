import assert from "node:assert/strict";
import test from "node:test";
import { beginPaymentAttempt, linkPaymentOrder, readPaymentAttempt, retirePaymentAttempt } from "../src/billingAttempt.js";

const KEY = "attempt";
const OLD_REQUEST = "11111111-1111-4111-8111-111111111111";
const OLD_ORDER = "22222222-2222-4222-8222-222222222222";
const NEW_REQUEST = "33333333-3333-4333-8333-333333333333";
const NEW_ORDER = "44444444-4444-4444-8444-444444444444";
function storage() {
  const values = new Map();
  return { getItem: (key) => values.get(key) ?? null,
    setItem: (key, value) => values.set(key, value), removeItem: (key) => values.delete(key) };
}

test("a terminal receipt retires only its own linked attempt", () => {
  const data = storage();
  beginPaymentAttempt(data, KEY, OLD_REQUEST);
  assert.equal(linkPaymentOrder(data, KEY, OLD_REQUEST, OLD_ORDER), true);
  assert.equal(retirePaymentAttempt(data, KEY, NEW_ORDER), false);
  assert.equal(readPaymentAttempt(data, KEY).request_id, OLD_REQUEST);
  assert.equal(retirePaymentAttempt(data, KEY, OLD_ORDER), true);
  assert.equal(readPaymentAttempt(data, KEY), null);
});

test("old receipt after lost new checkout response preserves the new retry UUID across reload", () => {
  const data = storage();
  beginPaymentAttempt(data, KEY, OLD_REQUEST);
  linkPaymentOrder(data, KEY, OLD_REQUEST, OLD_ORDER);
  // The second request reaches the server, but its response containing NEW_ORDER is lost.
  beginPaymentAttempt(data, KEY, NEW_REQUEST);
  // A reload still displays OLD_ORDER from the separately stored receipt.
  assert.equal(retirePaymentAttempt(data, KEY, OLD_ORDER), false);
  const reloaded = readPaymentAttempt(data, KEY);
  assert.deepEqual(reloaded, { request_id: NEW_REQUEST, order_id: null });
  // Retry reuses NEW_REQUEST and receives the existing server order, not a new request.
  assert.equal(linkPaymentOrder(data, KEY, reloaded.request_id, NEW_ORDER), true);
  assert.equal(retirePaymentAttempt(data, KEY, OLD_ORDER), false);
  assert.equal(readPaymentAttempt(data, KEY).request_id, NEW_REQUEST);
  assert.equal(retirePaymentAttempt(data, KEY, NEW_ORDER), true);
});

test("a delayed response cannot replace or retire a newer linked operation", () => {
  const data = storage();
  beginPaymentAttempt(data, KEY, OLD_REQUEST);
  beginPaymentAttempt(data, KEY, NEW_REQUEST);
  linkPaymentOrder(data, KEY, NEW_REQUEST, NEW_ORDER);
  assert.equal(linkPaymentOrder(data, KEY, OLD_REQUEST, OLD_ORDER), false);
  assert.equal(retirePaymentAttempt(data, KEY, OLD_ORDER), false);
  assert.deepEqual(readPaymentAttempt(data, KEY), { request_id: NEW_REQUEST, order_id: NEW_ORDER });
});

test("legacy UUID-only attempts remain reusable and cannot be cleared by an unrelated receipt", () => {
  const data = storage();
  data.setItem(KEY, NEW_REQUEST);
  assert.equal(retirePaymentAttempt(data, KEY, OLD_ORDER), false);
  assert.deepEqual(readPaymentAttempt(data, KEY), { request_id: NEW_REQUEST, order_id: null });
  assert.equal(linkPaymentOrder(data, KEY, NEW_REQUEST, NEW_ORDER), true);
  assert.equal(retirePaymentAttempt(data, KEY, NEW_ORDER), true);
});

test("invalid storage is rejected and failed persistence never pretends to save an attempt", () => {
  const data = storage();
  data.setItem(KEY, '{"request_id":"invalid","order_id":null}');
  assert.equal(readPaymentAttempt(data, KEY), null);
  assert.throws(() => beginPaymentAttempt(data, KEY, "invalid"));
  const blocked = { ...data, setItem: () => { throw new Error("storage unavailable"); } };
  assert.throws(() => beginPaymentAttempt(blocked, KEY, NEW_REQUEST), /storage unavailable/);
  assert.equal(readPaymentAttempt(data, KEY), null);
});

test("retiring an order fails conservatively if session storage cannot remove it", () => {
  const data = storage();
  beginPaymentAttempt(data, KEY, NEW_REQUEST);
  linkPaymentOrder(data, KEY, NEW_REQUEST, NEW_ORDER);
  const blocked = { ...data, removeItem: () => { throw new Error("storage unavailable"); } };
  assert.equal(retirePaymentAttempt(blocked, KEY, NEW_ORDER), false);
  assert.equal(readPaymentAttempt(data, KEY).request_id, NEW_REQUEST);
});
