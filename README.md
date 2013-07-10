# EvilGenius

This is a general purpose censorship environment simulator.

## What does it do?

To verify that ooniprobe-tests are working correctly, EvilGenius will provide a
series of virtual environments that simulate different censorship techniques
and run the tests against them.

## Getting started

### Setup the virtual machines

To setup the virtual machines you will need to go the `template/` directory and
run:

```
vagrant up
```

This will create 3 virtual machines: **probe**, **backend** and **router**.

### Running tests

You will then be able to control the various VMs you have setup.

To get access to the probe virtual machine you shall do:

```
vagrant ssh probe
```
