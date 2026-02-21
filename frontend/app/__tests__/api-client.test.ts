import { describe, it, expect } from "vitest";
import { wsUrl } from "@/app/utils/api-client";

describe("wsUrl", () => {
  it("should convert http to ws", () => {
    const url = wsUrl("test-run-id");
    expect(url).toBe("ws://localhost:8000/ws/council/test-run-id");
  });
});

describe("API client types", () => {
  it("should export runApi with expected methods", async () => {
    const { runApi } = await import("@/app/utils/api-client");
    expect(runApi.start).toBeDefined();
    expect(runApi.startFromBlueprint).toBeDefined();
    expect(runApi.status).toBeDefined();
    expect(runApi.approve).toBeDefined();
    expect(runApi.getState).toBeDefined();
  });

  it("should export councilApi with expected methods", async () => {
    const { councilApi } = await import("@/app/utils/api-client");
    expect(councilApi.list).toBeDefined();
    expect(councilApi.get).toBeDefined();
    expect(councilApi.create).toBeDefined();
    expect(councilApi.update).toBeDefined();
    expect(councilApi.delete).toBeDefined();
  });

  it("should export pdfApi with upload method", async () => {
    const { pdfApi } = await import("@/app/utils/api-client");
    expect(pdfApi.upload).toBeDefined();
  });
});
