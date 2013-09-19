# EvilGenius...

... is a general purpose censorship environment simulator.

## What does it do?

To verify that ooniprobe-tests are working correctly, EvilGenius will provide a
series of virtual environments that simulate different censorship techniques
and run the tests against them.

EvilGenius interacts with Vagrant, a developer-oriented interface for headless
VirtualBox.

When run with resources, EvilGenius will assemble a temporary virtual network
in VirtualBox (If you open the VirtualBox GUI when EvilGenius is running, you
can even watch it!) and run commands in it.

## Installation

EvilGenius depends on `python`, `pyyaml` and `vagrant`.

To install EvilGenius, after the dependencies are installed, just

```
git clone ...
```

and you're done.

## Synopsis

```
bin/evilgenius [--help] [--list] -n instrument1 -n instrument2 -c censorship [-v]
    [-L logdir] [-w workdir] [-d]
```

## Flags and options

The following flags and options are available in EvilGenius:
* `--help`: Displays usage information
* `--list`: List available resources, i.e. network measurement instruments and
    censorship providers
* `-n instrument`: Include a specific network measurement instrument. Currently
    about 120 network measurement instruments are supported simultaneously.
* `-c censorship`: Select a specific censorship provider. Currently only one
    censorship provider at a time is supported.
* `-v`: enable verbose output
* `-L`: Set log directory. If not specified, this defaults to the working 
    directory.
* `-w`: Set working Directory. If not specified, EvilGenius will create a
    temporary directory according to the conventions of your operating System.
* `-d`: Dry-Run. Write Vagrantfile to STDOUT and exit. Useful for debugging
    custom resource descriptor

## Resource Descriptors (How to roll your own)

### Network Measurement Instruments

Network measurement instruments are "probes" that are being run in the censored
environment. To build one, `cd` into the `resources` folder and create a
directory with the name for the new censorship box:

```
cd resources/network-measurement-instruments
mkdir myinstrument
```

Inside the instrument directory, create a yaml file with the filename 
`<name>.yml`.

```
touch myinstrument.yml
```

which you now begin to edit with the editor of your choice, `vim`.

Descriptor files are of a certain structure. As a template, you can use the
`ping` and traceroute descriptor files which are fairly basic.

Here's a further example with some explanations

```
# name of the Instrument, Identifies it for the `--list` command
name: Ping
# some description for the probe, appears in the `--list` command
description: Perform a simple ICMP Ping to goatse.cx
# box: defines the name of the Vagrant base box to use.
box: precise32

# This shall be run once when first setting up the network measurement virtual machine
install: sh /scripts/hello.sh

# optional, is run before the install command
before_install: 
        - echo "Hello, World!"
# optional, is run during the setup process after the network setup
after_install:
        - echo "Hello, World!"

# This is the command that executes the network measurment software once
# the whole network has been pulled up. 
run: ping -c 10 goatse.cx
```

### Censorship providers

Like network measurement instruments, censorship provider descriptor files
live in the `resources` folder, but since they're not network measurement
instruments, we put them in their own subfolder, namely `censorship-providers`.

We create a new file similar to what we dit with network managenment 
instruments above:

```
cd resources/censorship-provider
mkdir myprovider
cd myprovider
touch myprovider.yml
```

The only difference to network measurement instruments is that there is not
one single `run` sections, but start and stop sections where you can put the
start and stop commands for your censorship software. At the moment, they're
not used at all, in the meantime, just put the start command in `after_install`.

Here's an example with some documentation:

```
# name of the censorhip provider, appears in --list output
name: No Censorship
# description of the censorhip provider, appears in --list output
description: Do not perform censorship; use as base for your own providers.
# name of the vagrant base box to be used for this censorship provider
box: precise32

# This is run before the install command
before_install:
  - echo "Hello, World!"

# install command
install:
  - echo "Hello, World!"

# This is run after the install command and after the network setup 
after_install:
  - /sbin/sysctl -w net.ipv4.ip_forward=1
  - /sbin/iptables -F
  - /sbin/iptables --delete-chain
  - /sbin/iptables -t nat -F
  - /sbin/iptables -t nat --delete-chain
  - iptables --table nat --append POSTROUTING --out-interface eth0 -j MASQUERADE
  - iptables --append FORWARD --in-interface eth1 -j ACCEPT
  - echo "asdf"

# This shall be run every time the censorship vm starts
start: /sbin/sysctl -w net.ipv4.ip_forward=1

# This shall be run every time the censorship vm stops
stop: /sbin/sysctl -w net.ipv4.ip_forward=0
```
### Additional info on descriptors

The descriptors' directories are mounted into the vagrant box as `/script`.
This means you can write shell scripts and put them next to the descriptor
file.

You can execute them from the descriptor file via `/bin/bash /scripts/<script>`.

### Useful strategies for debugging descriptors

Writing resource descriptors can be tricky and time-consuming. Here are some
strategies that should facilitate debugging.

  * Start out from a template or very basic descriptor file.
  * Make a minimal network configuration, and save the `Vagrantfile` to an empty
    directory. then boot the network up by `cd`ing into that directory and
    calling `vagrant up`. Now you can watch the log scrolling by and see if
    something fails.
  * If something breaks and you're not sure why, remove the command from the
    descriptor file and boot the network up without it. then `vagrant ssh` into
    the box in question and try to execute it by hand.
