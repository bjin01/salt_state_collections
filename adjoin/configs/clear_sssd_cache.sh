#!/bin/bash
systemctl stop sssd
rm /var/lib/sss/db/*
systemctl restart sssd

