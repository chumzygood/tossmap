import { isIP } from 'node:net';

// Cloudflare supplies a bare IP address. Collapse IPv6 hosts to a canonical /64
// so changing an interface identifier cannot reset caller limits.
export function callerKey(address: string): string {
  const version = isIP(address);
  if (version === 4) return address;
  if (version !== 6 || address.includes('%')) return 'unknown';

  let input = address.toLowerCase();
  if (input.includes('.')) {
    const lastColon = input.lastIndexOf(':');
    const octets = input.slice(lastColon + 1).split('.').map(Number);
    input = input.slice(0, lastColon + 1) +
      ((octets[0] << 8) | octets[1]).toString(16) + ':' +
      ((octets[2] << 8) | octets[3]).toString(16);
  }
  const halves = input.split('::');
  const left = halves[0] ? halves[0].split(':') : [];
  const right = halves.length === 2 && halves[1] ? halves[1].split(':') : [];
  const groups = halves.length === 2
    ? [...left, ...Array(8 - left.length - right.length).fill('0'), ...right]
    : left;
  return groups.slice(0, 4).map(group => group.padStart(4, '0')).join(':') + '::/64';
}
