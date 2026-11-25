import {describe, expect, it} from 'vitest';
import {callerKey} from './caller';

describe('caller identity', () => {
  it('keeps IPv4 addresses distinct', () => {
    expect(callerKey('192.0.2.1')).toBe('192.0.2.1');
    expect(callerKey('192.0.2.2')).toBe('192.0.2.2');
  });
  it('normalizes compressed, expanded and mixed-case IPv6 addresses to /64', () => {
    const prefix = '2001:0db8:0000:0001::/64';
    expect(callerKey('2001:DB8:0:1::1')).toBe(prefix);
    expect(callerKey('2001:0db8:0000:0001:ffff:1234:5678:abcd')).toBe(prefix);
    expect(callerKey('2001:db8:0:2::1')).toBe('2001:0db8:0000:0002::/64');
    expect(callerKey('::1')).toBe('0000:0000:0000:0000::/64');
    expect(callerKey('2001:db8::')).toBe('2001:0db8:0000:0000::/64');
  });
  it('normalizes IPv4-mapped IPv6 forms as IPv6 /64', () => {
    expect(callerKey('::ffff:192.0.2.128')).toBe('0000:0000:0000:0000::/64');
    expect(callerKey('0:0:0:0:0:ffff:c000:280')).toBe('0000:0000:0000:0000::/64');
  });
  it('uses a shared fallback for invalid or missing addresses', () => {
    expect(callerKey('2001:db8:::1')).toBe('unknown');
    expect(callerKey('fe80::1%eth0')).toBe('unknown');
    expect(callerKey('')).toBe('unknown');
  });
});
