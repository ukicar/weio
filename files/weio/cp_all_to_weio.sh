#!/bin/bash

scp weio.py root@WEIO.local:/weio
scp -r static root@WEIO.local:/weio
scp IWList.py root@WEIO.local:/weio

