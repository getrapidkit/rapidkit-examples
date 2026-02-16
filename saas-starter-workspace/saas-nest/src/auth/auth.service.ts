import { Injectable } from '@nestjs/common';
import { randomBytes, createHash } from 'node:crypto';

type UserRecord = {
  id: string;
  email: string;
  passwordHash: string;
  fullName?: string;
};

type UserProfile = {
  userId: string;
  displayName?: string;
  timezone: string;
  biography?: string;
};

@Injectable()
export class AuthService {
  private usersByEmail = new Map<string, UserRecord>();
  private usersById = new Map<string, UserRecord>();
  private tokens = new Map<string, string>();
  private profiles = new Map<string, UserProfile>();

  register(payload: { email: string; password: string; fullName?: string }) {
    const email = payload.email.trim().toLowerCase();
    if (this.usersByEmail.has(email)) {
      throw new Error('Email already registered');
    }

    const user: UserRecord = {
      id: `user_${randomBytes(8).toString('hex')}`,
      email,
      passwordHash: this.hash(payload.password),
      fullName: payload.fullName,
    };
    this.usersByEmail.set(email, user);
    this.usersById.set(user.id, user);
    this.profiles.set(user.id, {
      userId: user.id,
      displayName: payload.fullName,
      timezone: 'UTC',
      biography: undefined,
    });

    const token = this.issueToken(user.id);
    return { user: this.publicUser(user), access_token: token, token_type: 'bearer' };
  }

  login(payload: { email: string; password: string }) {
    const email = payload.email.trim().toLowerCase();
    const user = this.usersByEmail.get(email);
    if (!user || user.passwordHash !== this.hash(payload.password)) {
      throw new Error('Invalid credentials');
    }
    const token = this.issueToken(user.id);
    return { user: this.publicUser(user), access_token: token, token_type: 'bearer' };
  }

  resolveUserByToken(token: string): UserRecord | null {
    const userId = this.tokens.get(token);
    if (!userId) {
      return null;
    }
    return this.usersById.get(userId) ?? null;
  }

  me(token: string) {
    const user = this.resolveUserByToken(token);
    if (!user) {
      return null;
    }
    return { user: this.publicUser(user) };
  }

  getProfile(token: string) {
    const user = this.resolveUserByToken(token);
    if (!user) {
      return null;
    }
    return this.profiles.get(user.id) ?? null;
  }

  updateProfile(token: string, patch: Partial<UserProfile>) {
    const user = this.resolveUserByToken(token);
    if (!user) {
      return null;
    }
    const current = this.profiles.get(user.id) ?? { userId: user.id, timezone: 'UTC' };
    const next = {
      ...current,
      ...patch,
      userId: user.id,
      timezone: patch.timezone ?? current.timezone ?? 'UTC',
    };
    this.profiles.set(user.id, next);
    return next;
  }

  private issueToken(userId: string): string {
    const token = randomBytes(24).toString('hex');
    this.tokens.set(token, userId);
    return token;
  }

  private hash(raw: string): string {
    return createHash('sha256').update(raw).digest('hex');
  }

  private publicUser(user: UserRecord) {
    return {
      id: user.id,
      email: user.email,
      full_name: user.fullName,
    };
  }
}