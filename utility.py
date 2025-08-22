# fun_utils_true.py
import datetime, psutil

def fmt_gb(n): return f"{n/(1024**3):.1f} GB"

def check_disk():
    for p in psutil.disk_partitions(all=False):
        try: u = psutil.disk_usage(p.mountpoint)
        except PermissionError: continue
        print(f"{p.device:<6} {fmt_gb(u.total):>8} {fmt_gb(u.used):>8} {fmt_gb(u.free):>8} {u.percent:>4}%  {p.mountpoint}")

def check_ram():
    m = psutil.virtual_memory()
    print(f"Total: {fmt_gb(m.total)}  Used: {fmt_gb(m.used)}  Free: {fmt_gb(m.available)}  {m.percent}%")

def check_uptime():
    boot = datetime.datetime.fromtimestamp(psutil.boot_time())
    d = datetime.datetime.now() - boot
    print(f"Uptime: {d.days}d {d.seconds//3600}h {(d.seconds//60)%60}m (since {boot:%Y-%m-%d %H:%M:%S})")

if __name__ == "__main__":
    check_disk(); print()
    check_ram(); print()
    check_uptime()
