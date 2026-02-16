import { ConflictException } from "@nestjs/common";
import { Test } from "@nestjs/testing";

import { UsersCoreModule } from "../../../../../src/modules/free/users/users_core/users-core.module";
import { UsersCoreService } from "../../../../../src/modules/free/users/users_core/users-core.service";

describe("UsersCoreModule Integration", () => {
  let service: UsersCoreService;

  beforeEach(async () => {
    const moduleRef = await Test.createTestingModule({
      imports: [UsersCoreModule],
    }).compile();

    service = moduleRef.get(UsersCoreService);
  });

  it("builds metadata from defaults", () => {
    const metadata = service.buildMetadata();
    expect(metadata.module).toBe("users_core");
    expect(metadata.title).toBe("Users Core");
    expect(metadata.features).toContain("user_registration");
    expect(metadata.supported_locales.length).toBeGreaterThan(0);
  });

  it("creates and retrieves users", async () => {
    const created = await service.createUser({
      email: "alice@example.com",
      fullName: "Alice Example",
    });

    expect(created.id).toBeDefined();
    expect(created.email).toBe("alice@example.com");

    const fetched = await service.getUser(created.id);
    expect(fetched).toEqual(created);

    const listed = await service.listUsers();
    expect(listed).toEqual([created]);
  });

  it("enforces unique email addresses", async () => {
    await service.createUser({ email: "duplicate@example.com" });

    await expect(
      service.createUser({ email: "duplicate@example.com" }),
    ).rejects.toBeInstanceOf(ConflictException);
  });

  it("produces health metadata", async () => {
    const payload = await service.resolveHealth();
    expect(payload.status).toBe("ok");
    expect(payload.module).toBe("users_core");
    expect(payload.features).toEqual(expect.arrayContaining(["user_registration"]));
  });
});
