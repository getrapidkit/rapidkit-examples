import { Test } from "@nestjs/testing";

import { ApiKeysModule } from "../../src/modules/free/auth/api_keys/api-keys.module";
import { ApiKeysService } from "../../src/modules/free/auth/api_keys/api-keys.service";

describe("ApiKeysModule", () => {
  it("registers the service", async () => {
    const moduleRef = await Test.createTestingModule({
      imports: [ApiKeysModule],
    }).compile();

    const service = moduleRef.get(ApiKeysService);
    expect(service).toBeDefined();
  });
});
