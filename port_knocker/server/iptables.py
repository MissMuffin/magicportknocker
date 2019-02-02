import iptc
from elevate import elevate
from port_knocker.util.security_logger import sec_logger

# add user port privileges to iptables (after successful authentication)
def open_ports(ip, ports):
    table = iptc.Table(iptc.Table.FILTER)
    chain = iptc.Chain(table, "INPUT")
    for port in ports:
        for proto in ["tcp", "udp"]:
            rule = iptc.Rule()
            rule.src = ip
            rule.protocol = proto
            rule.target = rule.create_target("ACCEPT")
            m = rule.create_match(proto)
            m.dport = port
            try:
                chain.delete_rule(rule)
            except:
                pass
            chain.insert_rule(rule)
    table.commit()
    sec_logger.info("opened ports {}".format(ports))

if __name__ == '__main__':
    # elevate this to root
    elevate(graphical=False)
    open_ports("127.0.0.3", ["44053"])