from app.utils.log_parser import parse_log

def test_parse_failed_login():
    raw = 'Jun 21 08:20:44 ubuntu sshd[1234]: Failed password for root from 10.10.10.12 port 22'
    result = parse_log(raw, 'auth.log')
    assert result.action == 'failed_login'
    assert result.username == 'root'
    assert result.source_ip == '10.10.10.12'
    assert result.severity == 'medium'

def test_parse_successful_login():
    raw = 'Jun 21 09:00:00 ubuntu sshd[5678]: Accepted password for alice from 192.168.1.5 port 22'
    result = parse_log(raw, 'auth.log')
    assert result.action == 'successful_login'
    assert result.username == 'alice'
    assert result.source_ip == '192.168.1.5'

def test_parse_sudo_failure():
    raw = 'Jun 21 10:00:00 ubuntu sudo[999]: pam_unix(sudo:auth): authentication failure; user=bob'
    result = parse_log(raw, 'auth.log')
    assert result.action == 'sudo_failure'
    assert result.severity == 'high'