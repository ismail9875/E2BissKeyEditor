from __future__ import absolute_import
try:
    # Python 2 compatibility
    from Components.Converter.Converter import Converter
    from Components.Element import cached
    from enigma import iServiceInformation, iPlayableService
    from Components.Converter.Poll import Poll
except ImportError:
    # Python 3 compatibility
    from Components.Converter.Converter import Converter
    from Components.Element import cached
    from enigma import iServiceInformation, iPlayableService
    from Components.Converter.Poll import Poll
import os
import subprocess
import traceback

# Initialize global variables to fix NameError
old_ecm_mtime = None
info = {}

# CAID mapping
cainfo = (
    ("0002", "0002", "18Crypt"), ("0100", "01FF", "Seca"), ("0500", "05FF", "Viaccess"),
    ("0600", "06FF", "Irdeto"), ("0B00", "0BFF", "Conax"), ("0D00", "0DFF", "Cryptoworks"),
    ("0E00", "0EFF", "PowerVu"), ("0900", "09FF", "NDS/Videoguard"), ("1702", "1702", "Betacrypt"),
    ("1722", "1722", "Betacrypt"), ("1762", "1762", "Betacrypt"), ("1700", "17FF", "Verimatrix"),
    ("1800", "18FF", "Nagravision"), ("2600", "26FF", "Biss"), ("4AEE", "4AEE", "Bulcrypt"),
    ("4AF8", "4AF8", "Griffin"), ("5581", "55FF", "Bulcrypt"), ("4AFC", "4AFC", "PanAccess"),
    ("4AEA", "4AEA", "Cryptoguard"), ("1EC0", "1ECF", "Cryptoguard"), ("5448", "5448", "Gospell VisionCrypt"),
    ("7AC8", "7AC8", "Gospell VisionCrypt"), ("7BE0", "7BE1", "DreCrypt"), ("A100", "A1FF", "RusCrypt"),
    ("0000", "0000", "no or unknown")
)

class E2BissKeyEditorCryptInfo(Poll, Converter):
    VPID = 0
    APID = 1
    PCRPID = 2
    PMTPID = 3
    TXTPID = 4
    CAID = 5
    PROV = 6
    ECMTIME = 7
    SOURCE = 8
    PROTOCOL = 9
    READER = 10
    SERVER = 11
    HOPS = 12
    CAIDNAME = 13
    CAMNAME = 14
    ECMINFO = 15
    FORMAT = 16
    PIDS = 17
    CAIDS = 18
    PMTTABLE = 19
    CONTROLWORDS = 20
    ECMPID = 21
    RESOLUTION = 22
    FPS = 23
    CHID = 24
    timespan = 1000

    def __init__(self, type):
        Poll.__init__(self)
        Converter.__init__(self, type)
        self.poll_interval = self.timespan
        self.poll_enabled = True
        if type == "VideoPID":
            self.type = self.VPID
        elif type == "AudioPID":
            self.type = self.APID
        elif type == "PCRPID":
            self.type = self.PCRPID
        elif type == "PMTPID":
            self.type = self.PMTPID
        elif type == "TXTPID":
            self.type = self.TXTPID
        elif type == "CAID":
            self.type = self.CAID
        elif type == "ProvID":
            self.type = self.PROV
        elif type == "EcmTime":
            self.type = self.ECMTIME
        elif type == "Source":
            self.type = self.SOURCE
        elif type == "Protocol":
            self.type = self.PROTOCOL
        elif type == "Reader":
            self.type = self.READER
        elif type == "Server":
            self.type = self.SERVER
        elif type == "Hops":
            self.type = self.HOPS
        elif type == "CaidName":
            self.type = self.CAIDNAME
        elif type == "CamName":
            self.type = self.CAMNAME
        elif type == "PIDs":
            self.type = self.PIDS
        elif type == "CAIDs":
            self.type = self.CAIDS
        elif type == "PMTTable":
            self.type = self.PMTTABLE
        elif type == "ControlWords":
            self.type = self.CONTROLWORDS
        elif type == "EcmPID":
            self.type = self.ECMPID
        elif type == "Resolution":
            self.type = self.RESOLUTION
        elif type == "FPS":
            self.type = self.FPS
        elif type == "ChID":
            self.type = self.CHID
        elif type == "EcmInfo" or type == "Default" or type == "" or type is None:
            self.type = self.ECMINFO
        else:
            self.type = self.FORMAT
            self.sfmt = type

    @cached
    def getText(self):
        try:
            service = self.source.service
            if not service:
                with open("/tmp/MetrixHDPids.log", "a") as f:
                    f.write("Service is None\n")
                return "No service available"

            info = service.info()
            if not info:
                with open("/tmp/MetrixHDPids.log", "a") as f:
                    f.write("Service info is None\n")
                return "No service available"

            result = ""
            ecm_info = self.ecmfile(service)
            caids = self.CaidList(service)
            is_fta = not caids and not ecm_info

            # Log ECM info for debugging
            with open("/tmp/MetrixHDPids.log", "a") as f:
                f.write(f"ECM Info: {ecm_info}\n")

            # PID and SID retrieval
            pids = {
                "Video PID": info.getInfo(iServiceInformation.sVideoPID) if info else -1,
                "Audio PID": info.getInfo(iServiceInformation.sAudioPID) if info else -1,
                "PCR PID": info.getInfo(iServiceInformation.sPCRPID) if info else -1,
                "PMT PID": info.getInfo(iServiceInformation.sPMTPID) if info else -1,
                "TXT PID": info.getInfo(iServiceInformation.sTXTPID) if info else -1,
                "SID": info.getInfo(iServiceInformation.sSID) if info else -1
            }
            for pid_name, pid_value in pids.items():
                if pid_value != -1:
                    pids[pid_name] = format(pid_value, '04X')
                else:
                    pids[pid_name] = "N/A"

            # Encryption info
            caid = ecm_info.get("caid", "") if ecm_info else ""
            if caid:
                caid = "%0.4X" % int(caid, 16)
            prov = ecm_info.get("prov", "") if ecm_info else ""
            if prov:
                prov = "%0.6X" % int(prov, 16) if prov.isdigit() else prov
            ecm_time = ecm_info.get("ecm time", "") if ecm_info else ""
            if ecm_time and "msec" in ecm_time:
                ecm_time = ecm_time.replace("msec", "ms")
            elif ecm_time:
                ecm_time = "%s ms" % ecm_time.replace(".", "").lstrip("0")
            source = ecm_info.get("source", "") if ecm_info else ""
            protocol = ecm_info.get("protocol", "") if ecm_info else ""
            reader = ecm_info.get("reader", "") if ecm_info else ""
            if len(reader) > 36:
                reader = "%s..." % reader[:35]
            server = ecm_info.get("server", "") if ecm_info else ""
            hops = ecm_info.get("hops", "") if ecm_info else ""
            if hops and hops != "0":
                hops = "Hops: %s" % hops
            caidname = self.CaidName(ecm_info)
            cw0 = ecm_info.get("cw0", "") if ecm_info else ""
            cw1 = ecm_info.get("cw1", "") if ecm_info else ""
            control_words = "\n".join([cw0, cw1]) if cw0 and cw1 else "" if not cw0 and not cw1 else cw0 or cw1
            ecm_pid = ecm_info.get("ecmpid", "") if ecm_info else ""
            if ecm_pid and ecm_pid.startswith("0x"):
                ecm_pid = ecm_pid[2:].upper()
            chid = ecm_info.get("chid", "") if ecm_info else ""
            if chid and chid.startswith("0x"):
                chid = chid[2:].upper()

            # Video information
            resolution = "N/A"
            try:
                width = info.getInfo(iServiceInformation.sVideoWidth)
                height = info.getInfo(iServiceInformation.sVideoHeight)
                if width > 0 and height > 0:
                    resolution = f"{width}x{height}"
                else:
                    with open("/proc/stb/vmpeg/0/resolution", "r") as f:
                        res = f.read().strip().split("x")
                        if len(res) == 2:
                            resolution = f"{res[0]}x{res[1]}"
            except:
                pass

            fps = "N/A"
            try:
                fps_val = info.getInfo(iServiceInformation.sFrameRate)
                if fps_val > 0:
                    fps = f"{fps_val // 1000}"
                else:
                    with open("/proc/stb/vmpeg/0/framerate", "r") as f:
                        fps_data = f.read().strip()
                        if fps_data.isdigit():
                            fps = str(int(fps_data) // 1000)
            except:
                pass

            # Handle specific types
            if self.type == self.VPID:
                return pids["Video PID"]
            elif self.type == self.APID:
                return pids["Audio PID"]
            elif self.type == self.PCRPID:
                return pids["PCR PID"]
            elif self.type == self.PMTPID:
                return pids["PMT PID"]
            elif self.type == self.TXTPID:
                return pids["TXT PID"]
            elif self.type == self.PIDS:
                return "VPID: %s APID: %s PCR: %s PMT: %s TXT: %s SID: %s" % (
                    pids["Video PID"], pids["Audio PID"], pids["PCR PID"],
                    pids["PMT PID"], pids["TXT PID"], pids["SID"])
            elif self.type == self.CAIDS:
                return "" if is_fta else caids
            elif self.type == self.CAID:
                return "" if is_fta else caid
            elif self.type == self.PROV:
                return "" if is_fta else prov
            elif self.type == self.ECMTIME:
                return "" if is_fta else ecm_time
            elif self.type == self.SOURCE:
                return "" if is_fta else source
            elif self.type == self.PROTOCOL:
                return "" if is_fta else protocol
            elif self.type == self.READER:
                return "" if is_fta else reader
            elif self.type == self.SERVER:
                return "" if is_fta else server
            elif self.type == self.HOPS:
                return "" if is_fta else hops
            elif self.type == self.CAIDNAME:
                return "" if is_fta else caidname
            elif self.type == self.CAMNAME:
                return self.CamName() or ""
            elif self.type == self.CONTROLWORDS:
                return "" if is_fta else control_words
            elif self.type == self.ECMPID:
                return "" if is_fta else ecm_pid
            elif self.type == self.RESOLUTION:
                return resolution
            elif self.type == self.FPS:
                return fps
            elif self.type == self.CHID:
                return "" if is_fta else chid
            elif self.type == self.PMTTABLE:
                pmt_pid = info.getInfo(iServiceInformation.sPMTPID) if info else -1
                if pmt_pid == -1:
                    return "PMT PID not available"
                try:
                    cmd = "dvbsnoop -s sec -n 1 -pd 4 -nph 0x%04X" % pmt_pid
                    output = subprocess.check_output(cmd, shell=True, text=True)
                    result = []
                    for line in output.splitlines():
                        if "stream_type" in line or "elementary_PID" in line or "ES_info" in line:
                            result.append(line.strip())
                    return " ".join(result) or "No PMT data"
                except subprocess.CalledProcessError:
                    return "Error reading PMT table"
            elif self.type == self.ECMINFO:
                if is_fta:
                    return "FTA service"
                return "CA: %s Prov: %s ChID: %s %s %s@%s %s CW: %s EcmPID: %s" % (
                    caid, prov, chid, caidname, reader, server, ecm_time, control_words, ecm_pid)
            elif self.type == self.FORMAT:
                result = ""
                params = self.sfmt.split(" ")
                for param in params:
                    if param:
                        if param[0] != "%":
                            result += param
                        elif param == "%VP":
                            result += pids["Video PID"]
                        elif param == "%AP":
                            result += pids["Audio PID"]
                        elif param == "%PP":
                            result += pids["PCR PID"]
                        elif param == "%MP":
                            result += pids["PMT PID"]
                        elif param == "%TP":
                            result += pids["TXT PID"]
                        elif param == "%SID":
                            result += pids["SID"]
                        elif param == "%CA":
                            result += "" if is_fta else caid
                        elif param == "%CAIDS":
                            result += "" if is_fta else caids
                        elif param == "%p":
                            result += "" if is_fta else prov
                        elif param == "%T":
                            result += "" if is_fta else ecm_time
                        elif param == "%O":
                            result += "" if is_fta else source
                        elif param == "%PR":
                            result += "" if is_fta else protocol
                        elif param == "%R":
                            result += "" if is_fta else reader
                        elif param == "%S":
                            result += "" if is_fta else server
                        elif param == "%H":
                            result += "" if is_fta else hops
                        elif param == "%CN":
                            result += "" if is_fta else caidname
                        elif param == "%CM":
                            result += self.CamName() or ""
                        elif param == "%CW":
                            result += "" if is_fta else control_words
                        elif param == "%EP":
                            result += "" if is_fta else ecm_pid
                        elif param == "%RES":
                            result += resolution
                        elif param == "%FPS":
                            result += fps
                        elif param == "%CHID":
                            result += "" if is_fta else chid
                        elif param == "%PIDS":
                            result += "VPID: %s APID: %s PCR: %s PMT: %s TXT: %s SID: %s" % (
                                pids["Video PID"], pids["Audio PID"], pids["PCR PID"],
                                pids["PMT PID"], pids["TXT PID"], pids["SID"])
                        elif param == "%CAIDS":
                            result += "" if is_fta else caids
                        elif param == "%t":
                            result += "\t"
                        elif param == "%n":
                            result += "\n"
                        elif param[1:].isdigit():
                            result = result.ljust(len(result) + int(param[1:]))
                        if result and result[-1] not in ("\t", "\n"):
                            result += " "
                return result.strip()
            return result or "No info available"
        except Exception as e:
            with open("/tmp/MetrixHDPids.log", "a") as f:
                f.write(f"Error in getText: {str(e)}\n{traceback.format_exc()}\n")
            return "No service available"

    text = property(getText)

    def CaidList(self, service):
        try:
            caids = []
            if service:
                info = service.info()
                if info:
                    caids = list(set(info.getInfoObject(iServiceInformation.sCAIDs)))
            return " ".join(format(x, '04X') for x in sorted(caids)) if caids else ""
        except Exception as e:
            with open("/tmp/MetrixHDPids.log", "a") as f:
                f.write(f"Error in CaidList: {str(e)}\n")
            return ""

    def CaidName(self, ecm_info):
        try:
            caidname = "Unknown"
            if ecm_info:
                caid = ecm_info.get("caid", "")
                if caid:
                    caid = "%0.4X" % int(caid, 16)
                    for ce in cainfo:
                        if ce[0] <= caid <= ce[1] or caid == ce[0]:
                            caidname = ce[2]
                            break
            return caidname
        except Exception as e:
            with open("/tmp/MetrixHDPids.log", "a") as f:
                f.write(f"Error in CaidName: {str(e)}\n")
            return "Unknown"

    def CamName(self):
        try:
            if os.path.exists("/tmp/cam.info"):
                with open("/tmp/cam.info", "r") as f:
                    return f.read().strip()
            elif os.path.exists("/etc/init.d/softcam"):
                with open("/etc/init.d/softcam", "r") as f:
                    for line in f:
                        if line.startswith("CAMNAME="):
                            return line.split('"')[1].strip()
            return ""
        except Exception as e:
            with open("/tmp/MetrixHDPids.log", "a") as f:
                f.write(f"Error in CamName: {str(e)}\n")
            return ""

    def ecmpath(self):
        try:
            for i in range(8, -1, -1):
                path = "/tmp/ecm%s.info" % i if i else "/tmp/ecm.info"
                if os.path.exists(path):
                    return path
            return None
        except Exception as e:
            with open("/tmp/MetrixHDPids.log", "a") as f:
                f.write(f"Error in ecmpath: {str(e)}\n")
            return None

    def ecmfile(self, service):
        global old_ecm_mtime, info
        ecm_info = {}
        ecmpath = self.ecmpath()
        if not ecmpath or not service:
            with open("/tmp/MetrixHDPids.log", "a") as f:
                f.write(f"No ECM path or service: {ecmpath}\n")
            return ecm_info
        try:
            ecm_mtime = os.stat(ecmpath).st_mtime
            if not os.stat(ecmpath).st_size:
                with open("/tmp/MetrixHDPids.log", "a") as f:
                    f.write(f"ECM file empty: {ecmpath}\n")
                return ecm_info
            if old_ecm_mtime and ecm_mtime == old_ecm_mtime:
                return info
            old_ecm_mtime = ecm_mtime
            with open(ecmpath, "r") as ecmf:
                ecm_content = ecmf.read()
                with open("/tmp/MetrixHDPids.log", "a") as f:
                    f.write(f"ECM file content ({ecmpath}):\n{ecm_content}\n")
                for line in ecm_content.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    x = line.lower().find("msec")
                    if x != -1:
                        ecm_info["ecm time"] = line[:x + 4]
                    else:
                        item = line.split(":", 1)
                        if len(item) > 1:
                            item[0] = item[0].strip().lower()
                            item[1] = item[1].strip()
                            if item[0] == "provider":
                                item[0] = "prov"
                                item[1] = item[1][2:] if item[1].startswith("0x") else item[1]
                            elif item[0] in ("ecm pid", "pid"):
                                item[0] = "ecmpid"
                                item[1] = item[1][2:].upper() if item[1].startswith("0x") else item[1]
                            elif item[0] == "response time":
                                ecm_info["source"] = "net"
                                parts = item[1].split()
                                ecm_info["ecm time"] = "%s msec" % parts[0]
                                if "[" in parts[-1]:
                                    ecm_info["server"] = parts[-1].split("[")[0].strip()
                                    ecm_info["protocol"] = parts[-1].split("[")[1].rstrip("]")
                                elif "(" in parts[-1]:
                                    ecm_info["server"] = parts[-1].split("(")[-1].split(":")[0]
                                    ecm_info["port"] = parts[-1].split(":")[-1].rstrip(")")
                            elif item[0] in ("hops", "from", "system", "provider", "chid"):
                                ecm_info[item[0]] = item[1]
                            elif item[0] == "source" and "net" in item[1]:
                                parts = item[1].split()
                                if len(parts) > 1 and "[" in parts[1]:
                                    ecm_info["protocol"] = parts[1][1:-1]
                            elif item[0] == "reader" and item[1] == "emu":
                                item[0] = "source"
                            elif item[0] == "protocol" and item[1] in ("emu", "constcw", "internal"):
                                ecm_info["source"] = "emu" if item[1] in ("emu", "constcw") else "sci"
                            elif item[0] == "using" and item[1] in ("emu", "sci"):
                                ecm_info["source"] = item[1]
                            elif item[0] == "address":
                                tt = item[1].find(":")
                                if tt != -1:
                                    ecm_info["server"] = item[1][:tt].strip()
                                    ecm_info["port"] = item[1][tt + 1:].strip()
                            elif item[0] in ("cw0", "cw1"):
                                ecm_info[item[0]] = item[1]
                            ecm_info[item[0]] = item[1]
                        else:
                            for key in ("caid", "ecmpid", "cw0", "cw1", "chid"):
                                if key not in ecm_info and key in line.lower():
                                    y = line.find(",") if "," in line else line.find(" ")
                                    if y != -1:
                                        ecm_info[key] = line[line.lower().find(key) + len(key) + 1:y].strip()
                                    else:
                                        ecm_info[key] = line[line.lower().find(key) + len(key) + 1:].strip()
            info = ecm_info
            return ecm_info
        except Exception as e:
            with open("/tmp/MetrixHDPids.log", "a") as f:
                f.write(f"Error in ecmfile: {str(e)}\n{traceback.format_exc()}\n")
            return {}

    def changed(self, what):
        try:
            Converter.changed(self, (self.CHANGED_POLL,))
        except Exception as e:
            with open("/tmp/MetrixHDPids.log", "a") as f:
                f.write(f"Error in changed: {str(e)}\n")