# This is the controller code. It acts as a simple Layer 2 learning switch.
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str

log = core.getLogger()

class LearningSwitch (object):
  def __init__ (self, connection):
    self.connection = connection
    connection.addListeners(self)
    self.mac_to_port = {}
    log.info("Switch %s has connected.", dpid_to_str(connection.dpid))

  def _handle_PacketIn (self, event):
    packet = event.parsed
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp
    in_port = packet_in.in_port
    src_mac = packet.src
    dst_mac = packet.dst

    # MAC Address Learning Logic
    if src_mac not in self.mac_to_port:
        self.mac_to_port[src_mac] = in_port
        log.info("Learned that %s is on port %s", src_mac, in_port)

    # Packet Forwarding Logic
    if dst_mac in self.mac_to_port:
        out_port = self.mac_to_port[dst_mac]

        # Dynamic Flow Rule Installation
        log.info("Installing flow for %s -> %s on port %s", src_mac, dst_mac, out_port)
        msg = of.ofp_flow_mod()
        msg.match.dl_dst = dst_mac
        msg.match.dl_src = src_mac
        msg.actions.append(of.ofp_action_output(port = out_port))
        msg.idle_timeout = 60
        msg.hard_timeout = 30
        self.connection.send(msg)

        self.send_packet(packet_in, out_port)
    else:
        log.info("Destination %s unknown. Flooding packet.", dst_mac)
        self.send_packet(packet_in, of.OFPP_FLOOD)

  def send_packet (self, packet_in, out_port):
    msg = of.ofp_packet_out()
    msg.data = packet_in
    action = of.ofp_action_output(port = out_port)
    msg.actions.append(action)
    self.connection.send(msg)

def launch ():
  def start_switch (event):
    log.info("Controlling new switch %s", event.connection.dpid)
    LearningSwitch(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
