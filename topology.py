#!/usr/bin/python3
"""
This script defines a custom Mininet topology for use with the 'mn' command.
"""
from mininet.topo import Topo

class SimpleTopo(Topo):
    "Simple topology with 3 hosts and 1 switch."

    def build(self):
        # Add hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')

        # Add switch
        s1 = self.addSwitch('s1')

        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(s1, h3)

# This dictionary allows Mininet to directly use our new topology
topos = { 'simple': ( lambda: SimpleTopo() ) }
