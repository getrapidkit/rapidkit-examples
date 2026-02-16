import { Module } from '@nestjs/common';
import { AuthController } from './auth.controller';
import { AuthService } from './auth.service';
import { UsersController } from './users.controller';

// <<<inject:auth-imports>>>

@Module({
  imports: [
    // <<<inject:auth-module>>>
  ],
  controllers: [AuthController, UsersController],
  providers: [AuthService],
  exports: [AuthService],
})
export class AuthModule { }