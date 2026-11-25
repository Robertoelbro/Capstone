import test from "node:test";
import assert from "node:assert/strict";
import { safeSubscriptionReturn } from "../src/billingReturn.js";

const receipt = "/suscripcion?orden=6a6662d5-f7da-49fe-85c9-f4dff4e33c27";
test("preserves the internal subscription receipt", () => {
  assert.equal(safeSubscriptionReturn(receipt), receipt);
  assert.equal(safeSubscriptionReturn("/suscripcion"), "/suscripcion");
});
test("rejects external destinations and encoded path tricks", () => {
  for (const path of ["https://untrusted.invalid", "//untrusted.invalid", "/%2fsuscripcion", "/suscripcion/extra", null, {}]) {
    assert.equal(safeSubscriptionReturn(path), null);
  }
});
test("rejects payment tokens, duplicate references and unvalidated order IDs", () => {
  for (const path of ["/suscripcion?token_ws=secret", receipt + "&orden=other", receipt + "&next=evil", receipt + "#token", "/suscripcion?orden=invalid"]) {
    assert.equal(safeSubscriptionReturn(path), null);
  }
});
