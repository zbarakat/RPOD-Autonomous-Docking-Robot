# SSH/Wi-Fi Recovery — Nov 23–24, 2026

**No credentials stored here.** Current goal: support user deferring Wi-Fi troubleshooting while retaining a reliable fallback.

## Verified working
- Windows laptop broadcasts Mobile Hotspot at 2.4 GHz with previously configured teammate WhiteSky SSID/password.
- Pi Zero 2 W connects and receives **192.168.137.141** on hotspot. Laptop hotspot gateway **192.168.137.1**.
- PowerShell from laptop: `ssh robot@192.168.137.141` worked; login username `robot`, hostname `romi-pi`.
- Windows cannot reliably resolve `romi-pi.local` even when Pi is reachable by IP. The Pi `ssh robot@romi-pi.local` command run on Pi only tests **self-SSH**.

## Current home network and unresolved state
- Home router SSID `NETGEAR10`, also advertising `NETGEAR10-5G`; **Pi supports only 2.4 GHz**, laptop may use 5 GHz on the same LAN.
- NETGEAR10 connection saved under NetworkManager, configured with `autoconnect` priority 50. First NETGEAR10 activation failed due missing secret; later user **did run** `sudo nmcli connection modify NETGEAR10 wifi-sec.key-mgmt wpa-psk wifi-sec.psk "$WIFI_PASS"` and `sudo nmcli connection up NETGEAR10`.
- The SSH session then reset, consistent with changing networks; home connection success is **unverified**. Don't assume the missing `.local` proves failure.

## When ready to resume
1. Keep the known Windows hotspot enabled as recovery path if available. From Pi shell:
   ```bash
   nmcli -f NAME,TYPE,DEVICE connection show --active
   nmcli device status
   hostname -I
   ip -4 addr show wlan0
   ```
2. If `NETGEAR10` active, obtain the actual **new LAN IP** from Pi output or home router client list. From Windows on same LAN, `ssh robot@<actual-address>` (literal placeholder must be replaced; do not type `PI_IP_ADDRESS` verbatim).
3. If not connected and access exists through hotspot, diagnose `NETGEAR10` profile and `journalctl -u NetworkManager` without exposing secret. Confirm PSK is stored via `sudo nmcli -f 802-11-wireless-security.psk-flags con show NETGEAR10` and correct 2.4 GHz AP, but **do not echo or upload password**.
4. Configure a robust Pi self-hosted access point for mobile testing only after a separate recovery method exists; Pi has one Wi-Fi radio.
5. The user explicitly said **"we'll come back to it"**, so do not force more network troubleshooting now.
