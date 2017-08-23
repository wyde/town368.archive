#!/bin/bash                                                                                                           
# Ref: https://shazi.info/%E8%90%AC%E7%94%A8%E7%9A%84-curl-%E6%A8%A1%E6%93%AC%E5%90%84%E7%A8%AE%E8%A8%AA%E5%95%8F%E7%8B%80%E6%B3%81%E3%80%81%E6%AA%A2%E6%B8%AC%E8%A8%AA%E5%95%8F%E9%80%9F%E5%BA%A6/
URL=$1
 
curl -o /dev/null -s -w \
"DNS Resolve: %{time_namelookup}\n\
Client -> Server: %{time_connect}\n\
Server Respon: %{time_starttransfer}\n\
Total time: %{time_total}\n" \
"${URL}"
