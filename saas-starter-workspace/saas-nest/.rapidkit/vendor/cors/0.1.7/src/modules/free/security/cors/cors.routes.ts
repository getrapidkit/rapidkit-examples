import { Type } from "@nestjs/common";

import { CorsController } from "./cors.controller";
import { CorsHealthController } from "../../../../health/cors.health";

export const CORS_ROUTES: Type[] = [
  CorsController,
  CorsHealthController,
];
