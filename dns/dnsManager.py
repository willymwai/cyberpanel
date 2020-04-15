#!/usr/local/CyberCP/bin/python
import os.path
import sys
import django
sys.path.append('/usr/local/CyberCP')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CyberCP.settings")
django.setup()
from django.shortcuts import render
from django.http import HttpResponse
import json
from plogical.dnsUtilities import DNS
from loginSystem.models import Administrator
import os
from .models import Domains,Records
from re import match,I,M
from plogical.mailUtilities import mailUtilities
from plogical.acl import ACLManager
import CloudFlare
import re
from plogical.CyberCPLogFileWriter import CyberCPLogFileWriter as logging

class DNSManager:
    defaultNameServersPath = '/home/cyberpanel/defaultNameservers'

    def loadCFKeys(self):
        cfFile = '%s%s' % (DNS.CFPath, self.admin.userName)
        data = open(cfFile, 'r').readlines()
        self.email = data[0].rstrip('\n')
        self.key = data[1].rstrip('\n')


    def loadDNSHome(self, request = None, userID = None):
        try:
            admin = Administrator.objects.get(pk=userID)
            return render(request, 'dns/index.html', {"type": admin.type})
        except BaseException as msg:
            return HttpResponse(str(msg))

    def createNameserver(self, request = None, userID = None):
        try:
            currentACL = ACLManager.loadedACL(userID)
            if ACLManager.currentContextPermission(currentACL, 'createNameServer') == 0:
                return ACLManager.loadError()

            mailUtilities.checkHome()

            if os.path.exists('/home/cyberpanel/powerdns'):
                return render(request, "dns/createNameServer.html", {"status": 1})
            else:
                return render(request, "dns/createNameServer.html", {"status": 0})

        except BaseException as msg:
            return HttpResponse(str(msg))

    def NSCreation(self, userID = None, data = None):
        try:
            admin = Administrator.objects.get(pk=userID)
            currentACL = ACLManager.loadedACL(userID)

            if ACLManager.currentContextPermission(currentACL, 'createNameServer') == 0:
                return ACLManager.loadErrorJson('NSCreation', 0)


            domainForNS = data['domainForNS']
            ns1 = data['ns1']
            ns2 = data['ns2']
            firstNSIP = data['firstNSIP']
            secondNSIP = data['secondNSIP']

            DNS.dnsTemplate(domainForNS, admin)

            newZone = Domains.objects.get(name=domainForNS)

            ## NS1


            record = Records(domainOwner=newZone,
                             domain_id=newZone.id,
                             name=ns1,
                             type="A",
                             content=firstNSIP,
                             ttl=3600,
                             prio=0,
                             disabled=0,
                             auth=1)
            record.save()

            ## NS2

            record = Records(domainOwner=newZone,
                             domain_id=newZone.id,
                             name=ns2,
                             type="A",
                             content=secondNSIP,
                             ttl=3600,
                             prio=0,
                             disabled=0,
                             auth=1)
            record.save()

            final_dic = {'NSCreation': 1, 'error_message': "None"}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)


        except BaseException as msg:
            final_dic = {'NSCreation': 0, 'error_message': str(msg)}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)

    def createDNSZone(self, request = None, userID = None):
        try:
            currentACL = ACLManager.loadedACL(userID)
            if ACLManager.currentContextPermission(currentACL, 'createDNSZone') == 0:
                return ACLManager.loadError()

            if os.path.exists('/home/cyberpanel/powerdns'):
                return render(request, 'dns/createDNSZone.html', {"status": 1})
            else:
                return render(request, 'dns/createDNSZone.html', {"status": 0})
        except BaseException as msg:
                return HttpResponse(str(msg))

    def zoneCreation(self, userID = None, data = None):
        try:
            admin = Administrator.objects.get(pk=userID)

            currentACL = ACLManager.loadedACL(userID)
            if ACLManager.currentContextPermission(currentACL, 'createDNSZone') == 0:
                return ACLManager.loadErrorJson('zoneCreation', 0)

            zoneDomain = data['zoneDomain']

            newZone = Domains(admin=admin, name=zoneDomain, type="NATIVE")
            newZone.save()

            content = "ns1." + zoneDomain + " hostmaster." + zoneDomain + " 1 10800 3600 604800 3600"

            soaRecord = Records(domainOwner=newZone,
                                domain_id=newZone.id,
                                name=zoneDomain,
                                type="SOA",
                                content=content,
                                ttl=3600,
                                prio=0,
                                disabled=0,
                                auth=1)
            soaRecord.save()

            final_dic = {'zoneCreation': 1}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)

        except BaseException as msg:
            final_dic = {'zoneCreation': 0, 'error_message': str(msg)}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)

    def addDeleteDNSRecords(self, request = None, userID = None):
        try:

            currentACL = ACLManager.loadedACL(userID)
            if ACLManager.currentContextPermission(currentACL, 'addDeleteRecords') == 0:
                return ACLManager.loadError()

            if not os.path.exists('/home/cyberpanel/powerdns'):
                return render(request, 'dns/addDeleteDNSRecords.html', {"status": 0})

            domainsList = ACLManager.findAllDomains(currentACL, userID)

            return render(request, 'dns/addDeleteDNSRecords.html', {"domainsList": domainsList, "status": 1})

        except BaseException as msg:
            return HttpResponse(str(msg))

    def getCurrentRecordsForDomain(self, userID = None, data = None):
        try:

            currentACL = ACLManager.loadedACL(userID)

            if ACLManager.currentContextPermission(currentACL, 'addDeleteRecords') == 0:
                return ACLManager.loadErrorJson('fetchStatus', 0)


            zoneDomain = data['selectedZone']
            currentSelection = data['currentSelection']

            admin = Administrator.objects.get(pk=userID)
            if ACLManager.checkOwnershipZone(zoneDomain, admin, currentACL) == 1:
                pass
            else:
                return ACLManager.loadErrorJson()

            domain = Domains.objects.get(name=zoneDomain)
            records = Records.objects.filter(domain_id=domain.id)

            fetchType = ""

            if currentSelection == 'aRecord':
                fetchType = 'A'
            elif currentSelection == 'aaaaRecord':
                fetchType = 'AAAA'
            elif currentSelection == 'cNameRecord':
                fetchType = 'CNAME'
            elif currentSelection == 'mxRecord':
                fetchType = 'MX'
            elif currentSelection == 'txtRecord':
                fetchType = 'TXT'
            elif currentSelection == 'spfRecord':
                fetchType = 'SPF'
            elif currentSelection == 'nsRecord':
                fetchType = 'NS'
            elif currentSelection == 'soaRecord':
                fetchType = 'SOA'
            elif currentSelection == 'srvRecord':
                fetchType = 'SRV'
            elif currentSelection == 'caaRecord':
                fetchType = 'CAA'

            json_data = "["
            checker = 0

            for items in records:
                if items.type == fetchType:
                    dic = {'id': items.id,
                           'type': items.type,
                           'name': items.name,
                           'content': items.content,
                           'priority': items.prio,
                           'ttl': items.ttl
                           }

                    if checker == 0:
                        json_data = json_data + json.dumps(dic)
                        checker = 1
                    else:
                        json_data = json_data + ',' + json.dumps(dic)
                else:
                    continue

            json_data = json_data + ']'
            final_json = json.dumps({'status': 1, 'fetchStatus': 1, 'error_message': "None", "data": json_data})
            return HttpResponse(final_json)

        except BaseException as msg:
            final_dic = {'status': 0, 'fetchStatus': 0, 'error_message': str(msg)}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)

    def addDNSRecord(self, userID = None, data = None):
        try:

            currentACL = ACLManager.loadedACL(userID)

            if ACLManager.currentContextPermission(currentACL, 'addDeleteRecords') == 0:
                return ACLManager.loadErrorJson('add_status', 0)

            zoneDomain = data['selectedZone']
            recordType = data['recordType']
            recordName = data['recordName']
            ttl = int(data['ttl'])

            admin = Administrator.objects.get(pk=userID)
            if ACLManager.checkOwnershipZone(zoneDomain, admin, currentACL) == 1:
                pass
            else:
                return ACLManager.loadErrorJson()

            zone = Domains.objects.get(name=zoneDomain)
            value = ""

            if recordType == "A":

                recordContentA = data['recordContentA']  ## IP or ponting value

                if recordName == "@":
                    value = zoneDomain
                ## re.match
                elif match(r'([\da-z\.-]+\.[a-z\.]{2,12}|[\d\.]+)([\/:?=&#]{1}[\da-z\.-]+)*[\/\?]?', recordName,
                           M | I):
                    value = recordName
                else:
                    value = recordName + "." + zoneDomain

                DNS.createDNSRecord(zone, value, recordType, recordContentA, 0, ttl)

            elif recordType == "MX":

                if recordName == "@":
                    value = zoneDomain
                ## re.match
                elif match(r'([\da-z\.-]+\.[a-z\.]{2,12}|[\d\.]+)([\/:?=&#]{1}[\da-z\.-]+)*[\/\?]?', recordName,
                           M | I):
                    value = recordName
                else:
                    value = recordName + "." + zoneDomain

                recordContentMX = data['recordContentMX']
                priority = data['priority']

                DNS.createDNSRecord(zone, value, recordType, recordContentMX, priority, ttl)

            elif recordType == "AAAA":

                if recordName == "@":
                    value = zoneDomain
                ## re.match
                elif match(r'([\da-z\.-]+\.[a-z\.]{2,12}|[\d\.]+)([\/:?=&#]{1}[\da-z\.-]+)*[\/\?]?', recordName,
                           M | I):
                    value = recordName
                else:
                    value = recordName + "." + zoneDomain

                recordContentAAAA = data['recordContentAAAA']  ## IP or ponting value

                DNS.createDNSRecord(zone, value, recordType, recordContentAAAA, 0, ttl)

            elif recordType == "CNAME":

                if recordName == "@":
                    value = zoneDomain
                ## re.match
                elif match(r'([\da-z\.-]+\.[a-z\.]{2,12}|[\d\.]+)([\/:?=&#]{1}[\da-z\.-]+)*[\/\?]?', recordName,
                           M | I):
                    value = recordName
                else:
                    value = recordName + "." + zoneDomain

                recordContentCNAME = data['recordContentCNAME']  ## IP or ponting value

                DNS.createDNSRecord(zone, value, recordType, recordContentCNAME, 0, ttl)

            elif recordType == "SPF":

                if recordName == "@":
                    value = zoneDomain
                ## re.match
                elif match(r'([\da-z\.-]+\.[a-z\.]{2,12}|[\d\.]+)([\/:?=&#]{1}[\da-z\.-]+)*[\/\?]?', recordName,
                           M | I):
                    value = recordName
                else:
                    value = recordName + "." + zoneDomain

                recordContentSPF = data['recordContentSPF']  ## IP or ponting value

                DNS.createDNSRecord(zone, value, recordType, recordContentSPF, 0, ttl)

            elif recordType == "TXT":

                if recordName == "@":
                    value = zoneDomain
                ## re.match
                elif match(r'([\da-z\.-]+\.[a-z\.]{2,12}|[\d\.]+)([\/:?=&#]{1}[\da-z\.-]+)*[\/\?]?', recordName,
                           M | I):
                    value = recordName
                else:
                    value = recordName + "." + zoneDomain

                recordContentTXT = data['recordContentTXT']  ## IP or ponting value

                DNS.createDNSRecord(zone, value, recordType, recordContentTXT, 0, ttl)

            elif recordType == "SOA":

                recordContentSOA = data['recordContentSOA']

                DNS.createDNSRecord(zone, recordName, recordType, recordContentSOA, 0, ttl)

            elif recordType == "NS":

                recordContentNS = data['recordContentNS']

                if recordContentNS == "@":
                    recordContentNS = "ns1." + zoneDomain
                ## re.match
                elif match(r'([\da-z\.-]+\.[a-z\.]{2,12}|[\d\.]+)([\/:?=&#]{1}[\da-z\.-]+)*[\/\?]?',
                           recordContentNS, M | I):
                    recordContentNS = recordContentNS
                else:
                    recordContentNS = recordContentNS + "." + zoneDomain

                DNS.createDNSRecord(zone, recordName, recordType, recordContentNS, 0, ttl)

            elif recordType == "SRV":

                if recordName == "@":
                    value = zoneDomain
                ## re.match
                elif match(r'([\da-z\.-]+\.[a-z\.]{2,12}|[\d\.]+)([\/:?=&#]{1}[\da-z\.-]+)*[\/\?]?', recordName,
                           M | I):
                    value = recordName
                else:
                    value = recordName + "." + zoneDomain

                recordContentSRV = data['recordContentSRV']
                priority = data['priority']

                DNS.createDNSRecord(zone, value, recordType, recordContentSRV, priority, ttl)

            elif recordType == "CAA":
                if recordName == "@":
                    value = zoneDomain
                ## re.match
                elif match(r'([\da-z\.-]+\.[a-z\.]{2,12}|[\d\.]+)([\/:?=&#]{1}[\da-z\.-]+)*[\/\?]?', recordName,
                           M | I):
                    value = recordName
                else:
                    value = recordName + "." + zoneDomain
                recordContentCAA = data['recordContentCAA']  ## IP or ponting value
                DNS.createDNSRecord(zone, value, recordType, recordContentCAA, 0, ttl)

            final_dic = {'status': 1, 'add_status': 1, 'error_message': "None"}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)

        except BaseException as msg:
            final_dic = {'status': 0, 'add_status': 0, 'error_message': str(msg)}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)

    def deleteDNSRecord(self, userID = None, data = None):
        try:
            currentACL = ACLManager.loadedACL(userID)

            if ACLManager.currentContextPermission(currentACL, 'addDeleteRecords') == 0:
                return ACLManager.loadErrorJson('delete_status', 0)

            id = data['id']

            delRecord = Records.objects.get(id=id)

            admin = Administrator.objects.get(pk=userID)

            if ACLManager.checkOwnershipZone(delRecord.domainOwner.name, admin, currentACL) == 1:
                pass
            else:
                return ACLManager.loadError()


            delRecord.delete()

            final_dic = {'status': 1, 'delete_status': 1, 'error_message': "None"}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)

        except BaseException as msg:
            final_dic = {'status': 0, 'delete_status': 0, 'error_message': str(msg)}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)

    def deleteDNSZone(self, request = None, userID = None):

        try:
            currentACL = ACLManager.loadedACL(userID)

            if ACLManager.currentContextPermission(currentACL, 'deleteZone') == 0:
                return ACLManager.loadError()

            if not os.path.exists('/home/cyberpanel/powerdns'):
                return render(request, 'dns/addDeleteDNSRecords.html', {"status": 0})

            domainsList = ACLManager.findAllDomains(currentACL, userID)

            return render(request, 'dns/deleteDNSZone.html', {"domainsList": domainsList, "status": 1})

        except BaseException as msg:
            return HttpResponse(str(msg))

    def submitZoneDeletion(self, userID = None, data = None):
        try:
            zoneDomain = data['zoneDomain']

            currentACL = ACLManager.loadedACL(userID)
            admin = Administrator.objects.get(pk=userID)
            if ACLManager.currentContextPermission(currentACL, 'deleteZone') == 0:
                return ACLManager.loadErrorJson('delete_status', 0)


            if ACLManager.checkOwnershipZone(zoneDomain, admin, currentACL) == 1:
                pass
            else:
                return ACLManager.loadError()

            delZone = Domains.objects.get(name=zoneDomain)
            admin = Administrator.objects.get(pk=userID)
            if currentACL['admin'] == 1:
                if delZone.admin != admin:
                    return ACLManager.loadErrorJson()

            delZone.delete()

            final_dic = {'delete_status': 1, 'error_message': "None"}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)

        except BaseException as msg:
            final_dic = {'delete_status': 0, 'error_message': str(msg)}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)

    def configureDefaultNameServers(self, request=None, userID=None):

        try:
            currentACL = ACLManager.loadedACL(userID)

            if currentACL['admin'] == 1:
                pass
            else:
                return ACLManager.loadError()

            if not os.path.exists('/home/cyberpanel/powerdns'):
                return render(request, 'dns/addDeleteDNSRecords.html', {"status": 0})

            data = {}
            data['domainsList'] = ACLManager.findAllDomains(currentACL, userID)
            data['status'] = 1

            if os.path.exists(DNSManager.defaultNameServersPath):
                nsData = open(DNSManager.defaultNameServersPath, 'r').readlines()
                try:
                    data['firstNS'] = nsData[0].rstrip('\n')
                except:
                    pass
                try:
                    data['secondNS'] = nsData[1].rstrip('\n')
                except:
                    pass
                try:
                    data['thirdNS'] = nsData[2].rstrip('\n')
                except:
                    pass
                try:
                    data['forthNS'] = nsData[3].rstrip('\n')
                except:
                    pass

            return render(request, 'dns/configureDefaultNameServers.html', data)

        except BaseException as msg:
            return HttpResponse(str(msg))


    def saveNSConfigurations(self, userID = None, data = None):
        try:
            currentACL = ACLManager.loadedACL(userID)

            if currentACL['admin'] == 1:
                pass
            else:
                return ACLManager.loadErrorJson()

            nsContent = ''

            try:
                nsContent = '%s\n%s\n%s\n%s\n' % (data['firstNS'].rstrip('\n'), data['secondNS'].rstrip('\n'), data['thirdNS'].rstrip('\n'), data['forthNS'].rstrip('\n'))
            except:
                try:
                    nsContent = '%s\n%s\n%s\n' % (data['firstNS'].rstrip('\n'), data['secondNS'].rstrip('\n'), data['thirdNS'].rstrip('\n'))
                except:
                    try:
                        nsContent = '%s\n%s\n' % (data['firstNS'].rstrip('\n'), data['secondNS'].rstrip('\n'))
                    except:
                        try:
                            nsContent = '%s\n' % (data['firstNS'].rstrip('\n'))
                        except:
                            pass


            writeToFile = open(DNSManager.defaultNameServersPath, 'w')
            writeToFile.write(nsContent.rstrip('\n'))
            writeToFile.close()


            final_dic = {'status': 1, 'error_message': "None"}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)

        except BaseException as msg:
            final_dic = {'status': 0, 'error_message': str(msg)}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)

    def addDeleteDNSRecordsCloudFlare(self, request = None, userID = None):
        try:

            currentACL = ACLManager.loadedACL(userID)
            if ACLManager.currentContextPermission(currentACL, 'addDeleteRecords') == 0:
                return ACLManager.loadError()

            if not os.path.exists('/home/cyberpanel/powerdns'):
                return render(request, 'dns/addDeleteDNSRecordsCloudFlare.html', {"status": 0})

            admin = Administrator.objects.get(pk=userID)

            CloudFlare = 0

            cfPath = '%s%s' %(DNS.CFPath, admin.userName)

            if os.path.exists(cfPath):
                CloudFlare = 1
                domainsList = ACLManager.findAllDomains(currentACL, userID)

                self.admin = admin
                self.loadCFKeys()

                return render(request, 'dns/addDeleteDNSRecordsCloudFlare.html',
                              {"domainsList": domainsList, "status": 1, 'CloudFlare': CloudFlare, 'cfEmail': self.email, 'cfToken': self.key})
            else:
                return render(request, 'dns/addDeleteDNSRecordsCloudFlare.html', {"status": 1, 'CloudFlare': CloudFlare})

        except BaseException as msg:
            return HttpResponse(str(msg))

    def saveCFConfigs(self, userID = None, data = None):
        try:
            cfEmail = data['cfEmail']
            cfToken = data['cfToken']
            cfSync = data['cfSync']

            currentACL = ACLManager.loadedACL(userID)

            if ACLManager.currentContextPermission(currentACL, 'addDeleteRecords') == 0:
                return ACLManager.loadErrorJson('status', 0)

            admin = Administrator.objects.get(pk=userID)
            cfPath = '%s%s' % (DNS.CFPath, admin.userName)

            writeToFile = open(cfPath, 'w')
            writeToFile.write('%s\n%s\n%s' % (cfEmail, cfToken, cfSync))
            writeToFile.close()

            os.chmod(cfPath, 0o600)

            final_dic = {'status': 1, 'error_message': "None"}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)

        except BaseException as msg:
            final_dic = {'status': 0, 'error_message': str(msg)}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)

    def getCurrentRecordsForDomainCloudFlare(self, userID = None, data = None):
        try:

            currentACL = ACLManager.loadedACL(userID)

            if ACLManager.currentContextPermission(currentACL, 'addDeleteRecords') == 0:
                return ACLManager.loadErrorJson('fetchStatus', 0)


            zoneDomain = data['selectedZone']
            currentSelection = data['currentSelection']

            admin = Administrator.objects.get(pk=userID)
            self.admin = admin

            if ACLManager.checkOwnershipZone(zoneDomain, admin, currentACL) == 1:
                pass
            else:
                return ACLManager.loadErrorJson()

            self.loadCFKeys()

            params = {'name': zoneDomain, 'per_page':50}
            cf = CloudFlare.CloudFlare(email=self.email,token=self.key)

            try:
                zones = cf.zones.get(params=params)
            except CloudFlare.CloudFlareAPIError as e:
                final_json = json.dumps({'status': 0, 'fetchStatus': 0, 'error_message': str(e), "data": '[]'})
                return HttpResponse(final_json)

            # there should only be one zone

            if len(zones) == 0:
                final_json = json.dumps({'status': 1, 'fetchStatus': 1, 'error_message': '', "data": '[]'})
                return HttpResponse(final_json)

            for zone in sorted(zones, key=lambda v: v['name']):
                zone_name = zone['name']
                zone_id = zone['id']

                fetchType = ""

                if currentSelection == 'aRecord':
                    fetchType = 'A'
                elif currentSelection == 'aaaaRecord':
                    fetchType = 'AAAA'
                elif currentSelection == 'cNameRecord':
                    fetchType = 'CNAME'
                elif currentSelection == 'mxRecord':
                    fetchType = 'MX'
                elif currentSelection == 'txtRecord':
                    fetchType = 'TXT'
                elif currentSelection == 'spfRecord':
                    fetchType = 'SPF'
                elif currentSelection == 'nsRecord':
                    fetchType = 'NS'
                elif currentSelection == 'soaRecord':
                    fetchType = 'SOA'
                elif currentSelection == 'srvRecord':
                    fetchType = 'SRV'
                elif currentSelection == 'caaRecord':
                    fetchType = 'CAA'

                try:
                    dns_records = cf.zones.dns_records.get(zone_id, params={'per_page':50, 'type':fetchType})
                except CloudFlare.exceptions.CloudFlareAPIError as e:
                    final_json = json.dumps({'status': 0, 'fetchStatus': 0, 'error_message': str(e), "data": '[]'})
                    return HttpResponse(final_json)

                prog = re.compile('\.*' + zone_name + '$')
                dns_records = sorted(dns_records, key=lambda v: prog.sub('', v['name']) + '_' + v['type'])

                json_data = "["
                checker = 0

                for dns_record in dns_records:
                    if dns_record['ttl'] == 1:
                        ttl = 'AUTO'
                    else:
                        ttl = dns_record['ttl']

                    dic = {'id': dns_record['id'],
                           'type': dns_record['type'],
                           'name': dns_record['name'],
                           'content': dns_record['content'],
                           'priority': '1400',
                           'ttl': ttl,
                           'proxy': dns_record['proxied'],
                           'proxiable': dns_record['proxiable']
                           }

                    if checker == 0:
                        json_data = json_data + json.dumps(dic)
                        checker = 1
                    else:
                        json_data = json_data + ',' + json.dumps(dic)


                json_data = json_data + ']'
                final_json = json.dumps({'status': 1, 'fetchStatus': 1, 'error_message': "None", "data": json_data})
                return HttpResponse(final_json)

        except BaseException as msg:
            final_dic = {'status': 0, 'fetchStatus': 0, 'error_message': str(msg)}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)

    def deleteDNSRecordCloudFlare(self, userID = None, data = None):
        try:
            currentACL = ACLManager.loadedACL(userID)

            if ACLManager.currentContextPermission(currentACL, 'addDeleteRecords') == 0:
                return ACLManager.loadErrorJson('fetchStatus', 0)

            zoneDomain = data['selectedZone']
            id = data['id']

            admin = Administrator.objects.get(pk=userID)
            self.admin = admin

            if ACLManager.checkOwnershipZone(zoneDomain, admin, currentACL) == 1:
                pass
            else:
                return ACLManager.loadErrorJson()

            self.loadCFKeys()

            params = {'name': zoneDomain, 'per_page': 50}
            cf = CloudFlare.CloudFlare(email=self.email, token=self.key)

            try:
                zones = cf.zones.get(params=params)
            except CloudFlare.CloudFlareAPIError as e:
                final_json = json.dumps({'status': 0, 'delete_status': 0, 'error_message': str(e), "data": '[]'})
                return HttpResponse(final_json)

            for zone in sorted(zones, key=lambda v: v['name']):
                zone_id = zone['id']

                cf.zones.dns_records.delete(zone_id, id)

                final_dic = {'status': 1, 'delete_status': 1, 'error_message': "None"}
                final_json = json.dumps(final_dic)
                return HttpResponse(final_json)

        except BaseException as msg:
            final_dic = {'status': 0, 'delete_status': 0, 'error_message': str(msg)}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)


    def addDNSRecordCloudFlare(self, userID = None, data = None):
        try:

            currentACL = ACLManager.loadedACL(userID)

            if ACLManager.currentContextPermission(currentACL, 'addDeleteRecords') == 0:
                return ACLManager.loadErrorJson('add_status', 0)

            zoneDomain = data['selectedZone']
            recordType = data['recordType']
            recordName = data['recordName']
            ttl = int(data['ttl'])

            admin = Administrator.objects.get(pk=userID)
            self.admin = admin
            if ACLManager.checkOwnershipZone(zoneDomain, admin, currentACL) == 1:
                pass
            else:
                return ACLManager.loadErrorJson()

            ## Get zone

            self.loadCFKeys()

            params = {'name': zoneDomain, 'per_page': 50}
            cf = CloudFlare.CloudFlare(email=self.email, token=self.key)

            try:
                zones = cf.zones.get(params=params)
            except CloudFlare.CloudFlareAPIError as e:
                final_json = json.dumps({'status': 0, 'delete_status': 0, 'error_message': str(e), "data": '[]'})
                return HttpResponse(final_json)

            for zone in sorted(zones, key=lambda v: v['name']):
                zone = zone['id']

                value = ""

                if recordType == "A":

                    recordContentA = data['recordContentA']  ## IP or ponting value

                    if recordName == "@":
                        value = zoneDomain
                    ## re.match
                    elif match(r'([\da-z\.-]+\.[a-z\.]{2,12}|[\d\.]+)([\/:?=&#]{1}[\da-z\.-]+)*[\/\?]?', recordName,
                               M | I):
                        value = recordName
                    else:
                        value = recordName + "." + zoneDomain

                    DNS.createDNSRecordCloudFlare(cf, zone, value, recordType, recordContentA, 0, ttl)

                elif recordType == "MX":

                    if recordName == "@":
                        value = zoneDomain
                    ## re.match
                    elif match(r'([\da-z\.-]+\.[a-z\.]{2,12}|[\d\.]+)([\/:?=&#]{1}[\da-z\.-]+)*[\/\?]?', recordName,
                               M | I):
                        value = recordName
                    else:
                        value = recordName + "." + zoneDomain

                    recordContentMX = data['recordContentMX']
                    priority = data['priority']

                    DNS.createDNSRecordCloudFlare(cf, zone, value, recordType, recordContentMX, priority, ttl)

                elif recordType == "AAAA":

                    if recordName == "@":
                        value = zoneDomain
                    ## re.match
                    elif match(r'([\da-z\.-]+\.[a-z\.]{2,12}|[\d\.]+)([\/:?=&#]{1}[\da-z\.-]+)*[\/\?]?', recordName,
                               M | I):
                        value = recordName
                    else:
                        value = recordName + "." + zoneDomain

                    recordContentAAAA = data['recordContentAAAA']  ## IP or ponting value

                    DNS.createDNSRecordCloudFlare(cf, zone, value, recordType, recordContentAAAA, 0, ttl)

                elif recordType == "CNAME":

                    if recordName == "@":
                        value = zoneDomain
                    ## re.match
                    elif match(r'([\da-z\.-]+\.[a-z\.]{2,12}|[\d\.]+)([\/:?=&#]{1}[\da-z\.-]+)*[\/\?]?', recordName,
                               M | I):
                        value = recordName
                    else:
                        value = recordName + "." + zoneDomain

                    recordContentCNAME = data['recordContentCNAME']  ## IP or ponting value

                    DNS.createDNSRecordCloudFlare(cf, zone, value, recordType, recordContentCNAME, 0, ttl)

                elif recordType == "SPF":

                    if recordName == "@":
                        value = zoneDomain
                    ## re.match
                    elif match(r'([\da-z\.-]+\.[a-z\.]{2,12}|[\d\.]+)([\/:?=&#]{1}[\da-z\.-]+)*[\/\?]?', recordName,
                               M | I):
                        value = recordName
                    else:
                        value = recordName + "." + zoneDomain

                    recordContentSPF = data['recordContentSPF']  ## IP or ponting value

                    DNS.createDNSRecordCloudFlare(cf, zone, value, recordType, recordContentSPF, 0, ttl)

                elif recordType == "TXT":

                    if recordName == "@":
                        value = zoneDomain
                    ## re.match
                    elif match(r'([\da-z\.-]+\.[a-z\.]{2,12}|[\d\.]+)([\/:?=&#]{1}[\da-z\.-]+)*[\/\?]?', recordName,
                               M | I):
                        value = recordName
                    else:
                        value = recordName + "." + zoneDomain

                    recordContentTXT = data['recordContentTXT']  ## IP or ponting value

                    DNS.createDNSRecordCloudFlare(cf, zone, value, recordType, recordContentTXT, 0, ttl)

                elif recordType == "SOA":

                    recordContentSOA = data['recordContentSOA']

                    DNS.createDNSRecordCloudFlare(cf, zone, recordName, recordType, recordContentSOA, 0, ttl)

                elif recordType == "NS":

                    recordContentNS = data['recordContentNS']

                    if recordContentNS == "@":
                        recordContentNS = "ns1." + zoneDomain
                    ## re.match
                    elif match(r'([\da-z\.-]+\.[a-z\.]{2,12}|[\d\.]+)([\/:?=&#]{1}[\da-z\.-]+)*[\/\?]?',
                               recordContentNS, M | I):
                        recordContentNS = recordContentNS
                    else:
                        recordContentNS = recordContentNS + "." + zoneDomain

                    DNS.createDNSRecordCloudFlare(cf, zone, recordName, recordType, recordContentNS, 0, ttl)

                elif recordType == "SRV":

                    if recordName == "@":
                        value = zoneDomain
                    ## re.match
                    elif match(r'([\da-z\.-]+\.[a-z\.]{2,12}|[\d\.]+)([\/:?=&#]{1}[\da-z\.-]+)*[\/\?]?', recordName,
                               M | I):
                        value = recordName
                    else:
                        value = recordName + "." + zoneDomain

                    recordContentSRV = data['recordContentSRV']
                    priority = data['priority']

                    DNS.createDNSRecordCloudFlare(cf, zone, value, recordType, recordContentSRV, priority, ttl)

                elif recordType == "CAA":
                    if recordName == "@":
                        value = zoneDomain
                    ## re.match
                    elif match(r'([\da-z\.-]+\.[a-z\.]{2,12}|[\d\.]+)([\/:?=&#]{1}[\da-z\.-]+)*[\/\?]?', recordName,
                               M | I):
                        value = recordName
                    else:
                        value = recordName + "." + zoneDomain
                    recordContentCAA = data['recordContentCAA']  ## IP or ponting value
                    DNS.createDNSRecordCloudFlare(cf, zone, value, recordType, recordContentCAA, 0, ttl)

                final_dic = {'status': 1, 'add_status': 1, 'error_message': "None"}
                final_json = json.dumps(final_dic)
                return HttpResponse(final_json)

        except BaseException as msg:
            final_dic = {'status': 0, 'add_status': 0, 'error_message': str(msg)}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)

    def syncCF(self, userID = None, data = None):
        try:

            currentACL = ACLManager.loadedACL(userID)

            if ACLManager.currentContextPermission(currentACL, 'addDeleteRecords') == 0:
                return ACLManager.loadErrorJson('add_status', 0)

            zoneDomain = data['selectedZone']

            admin = Administrator.objects.get(pk=userID)
            self.admin = admin

            if ACLManager.checkOwnershipZone(zoneDomain, admin, currentACL) == 1:
                pass
            else:
                return ACLManager.loadErrorJson()

            ## Get zone

            dns = DNS()

            status, error = dns.cfTemplate(zoneDomain, admin)

            if status == 1:
                final_dic = {'status': 1, 'error_message': 'None'}
                final_json = json.dumps(final_dic)
                return HttpResponse(final_json)
            else:
                final_dic = {'status': 0, 'error_message': error}
                final_json = json.dumps(final_dic)
                return HttpResponse(final_json)

        except BaseException as msg:
            final_dic = {'status': 0, 'error_message': str(msg)}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)


    def enableProxy(self, userID = None, data = None):
        try:
            currentACL = ACLManager.loadedACL(userID)

            if ACLManager.currentContextPermission(currentACL, 'addDeleteRecords') == 0:
                return ACLManager.loadErrorJson('fetchStatus', 0)

            zoneDomain = data['selectedZone']
            name = data['name']
            value = data['value']

            admin = Administrator.objects.get(pk=userID)
            self.admin = admin

            if ACLManager.checkOwnershipZone(zoneDomain, admin, currentACL) == 1:
                pass
            else:
                return ACLManager.loadErrorJson()

            self.loadCFKeys()

            params = {'name': zoneDomain, 'per_page': 50}
            cf = CloudFlare.CloudFlare(email=self.email, token=self.key)

            ## Get zone

            zones = cf.zones.get(params=params)

            zone = zones[0]

            ##

            zone_id = zone['id']

            params = {'name': name}
            dns_records = cf.zones.dns_records.get(zone_id, params=params)

            ##


            if value == True:
                new_r_proxied_flag = False
            else:
                new_r_proxied_flag = True

            for dns_record in dns_records:
                r_zone_id = dns_record['zone_id']
                r_id = dns_record['id']
                r_name = dns_record['name']
                r_type = dns_record['type']
                r_content = dns_record['content']
                r_ttl = dns_record['ttl']
                r_proxied = dns_record['proxied']
                r_proxiable = dns_record['proxiable']

                if r_proxied == new_r_proxied_flag:
                    # Nothing to do
                    continue

                dns_record_id = dns_record['id']

                new_dns_record = {
                    'zone_id': r_zone_id,
                    'id': r_id,
                    'type': r_type,
                    'name': r_name,
                    'content': r_content,
                    'ttl': r_ttl,
                    'proxied': new_r_proxied_flag
                }

                cf.zones.dns_records.put(zone_id, dns_record_id, data=new_dns_record)

                final_dic = {'status': 1, 'delete_status': 1, 'error_message': "None"}
                final_json = json.dumps(final_dic)
                return HttpResponse(final_json)

        except BaseException as msg:
            final_dic = {'status': 0, 'delete_status': 0, 'error_message': str(msg)}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)