import { Body, Controller, Get, Headers, HttpCode, HttpException, HttpStatus, Post } from '@nestjs/common';

import { AuthService } from './auth.service';

@Controller('auth')
export class AuthController {
  constructor(private readonly authService: AuthService) { }

  @Post('register')
  register(@Body() payload: { email: string; password: string; fullName?: string }) {
    try {
      return this.authService.register(payload);
    } catch (error) {
      throw new HttpException((error as Error).message, HttpStatus.CONFLICT);
    }
  }

  @Post('login')
  @HttpCode(200)
  login(@Body() payload: { email: string; password: string }) {
    try {
      return this.authService.login(payload);
    } catch {
      throw new HttpException('Invalid credentials', HttpStatus.UNAUTHORIZED);
    }
  }

  @Get('me')
  me(@Headers('authorization') authorization?: string) {
    const token = extractBearer(authorization);
    if (!token) {
      throw new HttpException('Authentication required', HttpStatus.UNAUTHORIZED);
    }
    const bundle = this.authService.me(token);
    if (!bundle) {
      throw new HttpException('Invalid token', HttpStatus.UNAUTHORIZED);
    }
    return bundle;
  }

  // <<<inject:auth-login>>>
  // <<<inject:auth-signup>>>
  // <<<inject:auth-refresh>>>
  // <<<inject:auth-logout>>>
  // <<<inject:auth-logout-all>>>
  // <<<inject:auth-me>>>
  // <<<inject:auth-protected>>>
  // <<<inject:auth-oauth-google>>>
  // <<<inject:auth-mfa-totp>>>
  // <<<inject:auth-email-verification>>>
  // <<<inject:auth-captcha>>>
  // <<<inject:auth-biometric>>>
  // <<<inject:auth-passwordless>>>
  // <<<inject:auth-federated>>>
  // <<<inject:auth-zero-trust>>>
}

function extractBearer(authorization?: string): string | null {
  if (!authorization || !authorization.toLowerCase().startsWith('bearer ')) {
    return null;
  }
  return authorization.split(' ', 2)[1] ?? null;
}