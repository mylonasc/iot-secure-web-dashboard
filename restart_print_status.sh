#!/bin/bash
systemctl restart nginx.service 
systemctl restart web_interface.service 
systemctl daemon-reload 
systemctl status nginx.service 
systemctl status web_interface.service
