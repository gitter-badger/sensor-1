from mock import Mock
from mock import MagicMock
import imp
import os
import sys

sys.modules['pyudev'] = Mock()
modulename = 'sitchlib'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")
file, pathname, description = imp.find_module(modulename, [modulepath])
fixturepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "../fixture/ceng.txt")
feedpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "../fixture/feed/")
sitchlib = imp.load_module(modulename, file, pathname, description)
sitch_feed_base = os.getenv('SITCH_FEED_BASE')
samp_sim = {'platform': u'AMLOGIC',
            'band': 'GSM850_MODE',
            'scan_finish': '2016-05-07 02:36:50',
            'scan_location': {'name': 'test_site'},
            'scanner_public_ip': '0.0.0.0',
            'scan_results': [
                {'bsic': '12', 'mcc': '310', 'rla': '00', 'lac': '178d',
                 'mnc': '411', 'txp': '05', 'rxl': '33',
                    'cell': '0', 'rxq': '00', 'ta': '255', 'cellid': '000f',
                    'arfcn': '0154'},
                {'cell': '1', 'rxl': '20', 'lac': '178d', 'bsic': '30',
                 'mnc': '411', 'mcc': '310', 'cellid': '0010',
                 'arfcn': '0128'},
                {'cell': '2', 'rxl': '10', 'lac': '178d', 'bsic': '00',
                 'mnc': '411', 'mcc': '310', 'cellid': '76e2',
                 'arfcn': '0179'},
                {'cell': '3', 'rxl': '10', 'lac': '178d', 'bsic': '51',
                 'mnc': '411', 'mcc': '310', 'cellid': '1208',
                 'arfcn': '0181'},
                {'cell': '4', 'rxl': '31', 'lac': '0000', 'bsic': '00',
                 'mnc': '', 'mcc': '', 'cellid': 'ffff',
                 'arfcn': '0237'},
                {'cell': '5', 'rxl': '23', 'lac': '0000', 'bsic': '00',
                 'mnc': '', 'mcc': '', 'cellid': 'ffff',
                    'arfcn': '0238'},
                {'cell': '6', 'rxl': '23', 'lac': '0000', 'bsic': '00',
                 'mnc': '', 'mcc': '', 'cellid': 'ffff',
                 'arfcn': '0236'}],
            'scan_start': '',
            'scan_program': 'GSM_MODEM'}


class TestGsmModemEnricher:
    def create_empty_state(self):
        state = {"gps": {},
                 "geoip": {},
                 "geo_distance_meters": 0,
                 "primary_cell": {"arfcn": "",
                                  "mcc": "",
                                  "mnc": "",
                                  "lac": "",
                                  "cid": ""}}
        return state

    def create_config(self):
        config = sitchlib.ConfigHelper
        config.__init__ = (MagicMock(return_value=None))
        config.device_id = "12345"
        config.feed_dir = "/tmp/"
        config.kal_threshold = "1000000"
        config.mcc_list = []
        config.feed_url_base = sitch_feed_base
        config.feed_dir = feedpath
        config.cgi_whitelist = []
        return config

    def create_modem_enricher(self):
        config = self.create_config()
        state = self.create_empty_state()
        enricher = sitchlib.GsmModemEnricher(state, config.feed_dir,
                                             config.cgi_whitelist)
        enricher.alerts = sitchlib.AlertManager()
        return enricher

    def test_convert_hex_targets(self):
        target_channel = samp_sim["scan_results"][0]
        enr = self.create_modem_enricher()
        result = enr.convert_hex_targets(target_channel)
        assert result["lac"] == "6029"
        assert result["cellid"] == "15"

    def test_str_to_float_badval(self):
        testval = "I AINT"
        result = sitchlib.Utility.str_to_float(testval)
        assert result is None

    def test_str_to_float_integer(self):
        testval = "12345"
        result = sitchlib.Utility.str_to_float(testval)
        assert result == 12345.0

    def test_str_to_float_float(self):
        testval = "12345.0010234"
        result = sitchlib.Utility.str_to_float(testval)
        assert result == 12345.0010234

    def test_geo_drift_check_suppress(self):
        """ We don't want to alarm if the starting value is zero """
        prior = 0
        threshold = 1
        current_gps = {"type": "Feature",
                       "geometry": {
                          "type": "Point",
                          "coordinates": [
                             3.41,
                             40.24]}}
        current_geoip = {"type": "Feature",
                         "geometry": {
                             "type": "Point",
                             "coordinates": [
                                 85.1835,
                                 35.244]}}
        result = sitchlib.Enricher.geo_drift_check(prior,
                                                   current_geoip,
                                                   current_gps,
                                                   threshold)
        assert not result

    def test_geo_drift_check_alarm(self):
        """ Make sure we throw alarms """
        prior = 1
        threshold = 1
        current_gps = {"type": "Feature",
                       "geometry": {
                          "type": "Point",
                          "coordinates": [
                             3.41,
                             40.24]}}
        current_geoip = {"type": "Feature",
                         "geometry": {
                             "type": "Point",
                             "coordinates": [
                                 85.1835,
                                 35.244]}}
        result = sitchlib.Enricher.geo_drift_check(prior,
                                                   current_geoip,
                                                   current_gps,
                                                   threshold)
        assert result

    def test_geo_drift_check_ok(self):
        """ If all is well, we return None """
        """ Make sure we throw alarms """
        prior = 1
        threshold = 6955000
        current_gps = {"type": "Feature",
                       "geometry": {
                          "type": "Point",
                          "coordinates": [
                             3.41,
                             40.24]}}
        current_geoip = {"type": "Feature",
                         "geometry": {
                             "type": "Point",
                             "coordinates": [
                                 85.1835,
                                 35.244]}}
        result = sitchlib.Enricher.geo_drift_check(prior,
                                                   current_geoip,
                                                   current_gps,
                                                   threshold)
        assert not result

    def test_unit_enrich_gsm_modem_primary_bts_changed_false(self):
        gsm_enr = sitchlib.GsmModemEnricher
        prior_bts = {'mcc': '310', 'lac': '178d',
                     'mnc': '411', 'cellid': '000f'}
        channel = {'bsic': '12', 'mcc': '310', 'rla': '00', 'lac': '178d',
                   'mnc': '411', 'txp': '05', 'rxl': '33',
                   'cell': '0', 'rxq': '00', 'ta': '255', 'cellid': '000f',
                   'arfcn': '0154'}
        channel["cgi_str"] = "1:2:3:4"
        cgi_whitelist = []
        assert gsm_enr.primary_bts_changed(prior_bts, channel,
                                           cgi_whitelist) is False

    def test_unit_enrich_gsm_modem_primary_bts_changed_true(self):
        gsm_enr = sitchlib.GsmModemEnricher
        prior_bts = {"mcc": "310", "mnc": "411", "lac": "234", "cellid": "22"}
        channel = {"mcc": "310", "mnc": "411", "lac": "234", "cellid": "23"}
        channel["cgi_str"] = "310:411:234:23"
        cgi_whitelist = []
        assert gsm_enr.primary_bts_changed(prior_bts, channel,
                                           cgi_whitelist) is True

    def test_unit_enrich_gsm_modem_primary_bts_changed_suppressed(self):
        gsm_enr = sitchlib.GsmModemEnricher
        prior_bts = {"mcc": "310", "mnc": "411", "lac": "234", "cellid": "22"}
        channel = {"mcc": "310", "mnc": "411", "lac": "234", "cellid": "23"}
        channel["cgi_str"] = "310:411:234:23"
        cgi_whitelist = ["310:411:234:22", "310:411:234:23"]
        assert gsm_enr.primary_bts_changed(prior_bts, channel,
                                           cgi_whitelist) is False
