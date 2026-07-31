#!/usr/bin/env python3
"""
تبدیل کانفیگ V2Ray به لینک اشتراک (vmess://, vless://, trojan://)
Convert V2Ray configs to share links
"""

import json
import base64
import sys
import os
import glob


def config_to_share_link(config_data):
    """تبدیل یک کانفیگ به لینک اشتراک"""
    try:
        # Handle both full config and single config
        if isinstance(config_data, list):
            # If it's a list, take the first one or process each
            results = []
            for cfg in config_data:
                link = _extract_single_link(cfg)
                if link:
                    results.append(link)
            return results
        else:
            link = _extract_single_link(config_data)
            return [link] if link else []
    except Exception as e:
        print(f"Error: {e}")
        return []


def _extract_single_link(cfg):
    """استخراج لینک از یک کانفیگ"""
    try:
        remarks = cfg.get('remarks', cfg.get('name', 'V2Ray Config'))
        outbounds = cfg.get('outbounds', cfg.get('config', {}).get('outbounds', []))
        
        for outbound in outbounds:
            protocol = outbound.get('protocol', '')
            
            # ==================== VLESS ====================
            if protocol == 'vless':
                return _make_vless_link(outbound, remarks)
            
            # ==================== TROJAN ====================
            elif protocol == 'trojan':
                return _make_trojan_link(outbound, remarks)
            
            # ==================== VMESS ====================
            elif protocol == 'vmess':
                return _make_vmess_link(outbound, remarks)
            
            # ==================== SHADOWSOCKS ====================
            elif protocol == 'shadowsocks':
                return _make_ss_link(outbound, remarks)
        
        return None
    except Exception as e:
        print(f"Error extracting link: {e}")
        return None


def _make_vless_link(outbound, remarks):
    """ساخت لینک vless://"""
    settings = outbound.get('settings', {})
    vnext = settings.get('vnext', [{}])[0]
    address = vnext.get('address', '')
    port = vnext.get('port', 80)
    user = vnext.get('users', [{}])[0]
    user_id = user.get('id', '')
    encryption = user.get('encryption', 'none')
    
    # Stream settings
    stream = outbound.get('streamSettings', {})
    network = stream.get('network', 'tcp')
    security = stream.get('security', 'none')
    
    # Build query params
    params = {
        'encryption': encryption,
        'security': security,
        'type': network
    }
    
    # Network specific params
    if network == 'ws':
        ws = stream.get('wsSettings', {})
        path = ws.get('path', '')
        host = ws.get('host', '') or ws.get('headers', {}).get('Host', '')
        if path:
            params['path'] = path
        if host:
            params['host'] = host
    
    elif network == 'grpc':
        grpc = stream.get('grpcSettings', {})
        serviceName = grpc.get('serviceName', '')
        if serviceName:
            params['serviceName'] = serviceName
    
    elif network == 'tcp':
        tcp = stream.get('tcpSettings', {})
        header = tcp.get('header', {})
        if header.get('type') == 'http':
            path = header.get('http', {}).get('path', '/')
            host = header.get('http', {}).get('host', [''])[0]
            params['path'] = path
            if host:
                params['host'] = host
    
    elif network == 'h2' or network == 'http':
        h2 = stream.get('h2Settings', {}) or stream.get('httpSettings', {})
        path = h2.get('path', '')
        host = h2.get('host', '')
        if path:
            params['path'] = path
        if host:
            params['host'] = host
    
    # Security specific params
    if security == 'tls':
        tls = stream.get('tlsSettings', {})
        sni = tls.get('serverName', '')
        fp = tls.get('fingerprint', '')
        alpn = ','.join(tls.get('alpn', []))
        if sni:
            params['sni'] = sni
        if fp:
            params['fp'] = fp
        if alpn:
            params['alpn'] = alpn
    
    elif security == 'reality':
        reality = stream.get('realitySettings', {})
        sni = reality.get('serverNames', [''])[0]
        fp = reality.get('fingerprint', '')
        pbk = reality.get('publicKey', '')
        sid = reality.get('shortId', '')
        spx = reality.get('spiderX', '')
        if sni:
            params['sni'] = sni
        if fp:
            params['fp'] = fp
        if pbk:
            params['pbk'] = pbk
        if sid:
            params['sid'] = sid
        if spx:
            params['spx'] = spx
    
    # Build URL
    query = '&'.join([f"{k}={v}" for k, v in params.items()])
    encoded_remarks = remarks.replace('#', '%23').replace(' ', '%20')
    
    return f"vless://{user_id}@{address}:{port}?{query}#{encoded_remarks}"


def _make_trojan_link(outbound, remarks):
    """ساخت لینک trojan://"""
    settings = outbound.get('settings', {})
    servers = settings.get('servers', [])
    
    if not servers:
        return None
    
    server = servers[0]
    address = server.get('address', '')
    port = server.get('port', 443)
    password = server.get('password', '')
    
    # Stream settings
    stream = outbound.get('streamSettings', {})
    network = stream.get('network', 'tcp')
    security = stream.get('security', 'tls')
    
    # Build query params
    params = {
        'type': network,
        'security': security
    }
    
    # Network specific params
    if network == 'ws':
        ws = stream.get('wsSettings', {})
        path = ws.get('path', '')
        host = ws.get('host', '') or ws.get('headers', {}).get('Host', '')
        if path:
            params['path'] = path
        if host:
            params['host'] = host
    
    elif network == 'grpc':
        grpc = stream.get('grpcSettings', {})
        serviceName = grpc.get('serviceName', '')
        if serviceName:
            params['serviceName'] = serviceName
    
    # Security specific params
    if security == 'tls':
        tls = stream.get('tlsSettings', {})
        sni = tls.get('serverName', '')
        fp = tls.get('fingerprint', '')
        if sni:
            params['sni'] = sni
        if fp:
            params['fp'] = fp
    
    # Build URL
    query = '&'.join([f"{k}={v}" for k, v in params.items()])
    encoded_remarks = remarks.replace('#', '%23').replace(' ', '%20')
    
    return f"trojan://{password}@{address}:{port}?{query}#{encoded_remarks}"


def _make_vmess_link(outbound, remarks):
    """ساخت لینک vmess://"""
    settings = outbound.get('settings', {})
    vnext = settings.get('vnext', [{}])[0]
    address = vnext.get('address', '')
    port = vnext.get('port', 443)
    user = vnext.get('users', [{}])[0]
    user_id = user.get('id', '')
    alter_id = user.get('alterId', 0)
    security = user.get('security', 'auto')
    
    # Stream settings
    stream = outbound.get('streamSettings', {})
    network = stream.get('network', 'tcp')
    tls_security = stream.get('security', 'none')
    
    # Build vmess object
    vmess_obj = {
        'v': '2',
        'ps': remarks,
        'add': address,
        'port': str(port),
        'id': user_id,
        'aid': str(alter_id),
        'net': network,
        'type': 'none',
        'host': '',
        'path': '',
        'tls': '',
        'sni': '',
        'fp': ''
    }
    
    # Network specific params
    if network == 'ws':
        ws = stream.get('wsSettings', {})
        vmess_obj['path'] = ws.get('path', '')
        vmess_obj['host'] = ws.get('host', '') or ws.get('headers', {}).get('Host', '')
    
    elif network == 'grpc':
        grpc = stream.get('grpcSettings', {})
        vmess_obj['path'] = grpc.get('serviceName', '')
    
    # Security params
    if tls_security == 'tls':
        vmess_obj['tls'] = 'tls'
        tls = stream.get('tlsSettings', {})
        vmess_obj['sni'] = tls.get('serverName', '')
        vmess_obj['fp'] = tls.get('fingerprint', '')
    
    elif tls_security == 'reality':
        vmess_obj['tls'] = 'reality'
        reality = stream.get('realitySettings', {})
        vmess_obj['sni'] = reality.get('serverNames', [''])[0]
        vmess_obj['fp'] = reality.get('fingerprint', '')
        vmess_obj['pbk'] = reality.get('publicKey', '')
        vmess_obj['sid'] = reality.get('shortId', '')
        vmess_obj['spx'] = reality.get('spiderX', '')
    
    # Encode to base64
    vmess_json = json.dumps(vmess_obj, ensure_ascii=False)
    vmess_b64 = base64.b64encode(vmess_json.encode('utf-8')).decode('utf-8')
    
    return f"vmess://{vmess_b64}"


def _make_ss_link(outbound, remarks):
    """ساخت لینک ss://"""
    settings = outbound.get('settings', {})
    servers = settings.get('servers', [])
    
    if not servers:
        return None
    
    server = servers[0]
    address = server.get('address', '')
    port = server.get('port', 443)
    method = server.get('method', 'aes-256-gcm')
    password = server.get('password', '')
    
    # Encode userinfo
    userinfo = base64.b64encode(f"{method}:{password}".encode()).decode()
    
    encoded_remarks = remarks.replace('#', '%23').replace(' ', '%20')
    
    return f"ss://{userinfo}@{address}:{port}#{encoded_remarks}"


def process_file(input_file, output_file=None):
    """پردازش فایل ورودی"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse as JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {input_file}")
            return []
        
        # Process config(s)
        links = config_to_share_link(data)
        
        if not links:
            print(f"Warning: No links generated from {input_file}")
            return []
        
        # Output
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                for link in links:
                    f.write(link + '\n')
            print(f"Saved {len(links)} links to {output_file}")
        
        return links
        
    except Exception as e:
        print(f"Error processing {input_file}: {e}")
        return []


def process_directory(input_dir, output_file):
    """پردازش تمام فایل‌های JSON در پوشه"""
    all_links = []
    
    # Find all JSON files
    json_files = glob.glob(os.path.join(input_dir, '*.json'))
    
    if not json_files:
        print(f"No JSON files found in {input_dir}")
        return []
    
    print(f"Found {len(json_files)} JSON files")
    
    for json_file in sorted(json_files):
        print(f"Processing: {os.path.basename(json_file)}")
        links = process_file(json_file)
        all_links.extend(links)
    
    # Save all links
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            for link in all_links:
                f.write(link + '\n')
        print(f"\nTotal: {len(all_links)} links saved to {output_file}")
    
    return all_links


def create_subscription(links, output_file):
    """ساخت فایل اشتراک (base64 encoded)"""
    # Join all links with newlines
    content = '\n'.join(links)
    
    # Encode to base64
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    # Save
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(encoded)
    
    print(f"Subscription file created: {output_file}")
    return encoded


def main():
    """تابع اصلی"""
    if len(sys.argv) < 2:
        print("""
🔧 V2Ray Config to Share Link Converter
========================================

Usage:
  python3 convert_to_links.py <input> [output]

Examples:
  python3 convert_to_links.py config.json
  python3 convert_to_links.py config.json links.txt
  python3 convert_to_links.py ./configs/ links.txt
  python3 convert_to_links.py ./configs/ sub.txt --sub

Input:
  - Single JSON file
  - Directory of JSON files

Output:
  - Text file with share links (one per line)
  - With --sub flag: base64 encoded subscription file
        """)
        return
    
    input_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'links.txt'
    create_sub = '--sub' in sys.argv
    
    # Process input
    if os.path.isdir(input_path):
        links = process_directory(input_path, None)
    elif os.path.isfile(input_path):
        links = process_file(input_path, None)
    else:
        print(f"Error: {input_path} not found")
        return
    
    if not links:
        print("No links generated!")
        return
    
    # Save links
    with open(output_file, 'w', encoding='utf-8') as f:
        for link in links:
            f.write(link + '\n')
    print(f"\nSaved {len(links)} share links to {output_file}")
    
    # Create subscription if requested
    if create_sub:
        sub_file = output_file.replace('.txt', '_sub.txt')
        create_subscription(links, sub_file)


if __name__ == '__main__':
    main()
