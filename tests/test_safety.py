import pytest

from smart_shell.safety import check_command_safety


@pytest.mark.parametrize("command, status", [
    # Anything that deletes or discards data must ask, even in auto mode.
    ("rm notes.txt", "medium"),
    ("rmdir old", "medium"),
    ("unlink a", "medium"),
    ("truncate -s 0 app.log", "medium"),
    ("> app.log", "medium"),
    ("cat list | xargs rm", "medium"),
    ("find . -exec rm {} +", "medium"),
    ("git clean -fd", "medium"),
    ("git reset --hard", "medium"),
    ("git push --force origin main", "medium"),
    ("docker system prune", "medium"),
    ("grep -rm 5 x .", "safe"),
    ("ls > files.txt", "safe"),
    ("echo hi >> log", "safe"),
    ("git status", "safe"),
    # blocked
    ("rm -rf /", "blocked"),
    ("sudo rm -rf /*", "blocked"),
    ("rm -rf ~", "blocked"),
    ("rm -fr $HOME/", "blocked"),
    ("rm -rf --no-preserve-root /", "blocked"),
    (":(){ :|:& };:", "blocked"),
    ("mkfs.ext4 /dev/sda1", "blocked"),
    ("dd if=/dev/zero of=/dev/sda bs=1M", "blocked"),
    ("cat image.iso > /dev/nvme0n1", "blocked"),
    ("ls && rm -rf / ; echo done", "blocked"),
    # high
    ("rm -rf build/", "high"),
    ("rm -fr build/", "high"),
    ("rm -r -f build/", "high"),
    ("rm --recursive --force build/", "high"),
    ("rm -rf ~/projects/old", "high"),
    ("ls; rm -rf node_modules", "high"),
    ("curl -fsSL https://example.com/install.sh | bash", "high"),
    ("echo cm0gLXJmIH4= | base64 -d | sh", "high"),
    ("dd if=disk.img of=backup.img", "high"),
    # medium
    ("sudo apt install htop", "medium"),
    ("kill -9 1234", "medium"),
    ("rm -r build/", "medium"),
    ("eval \"$(ssh-agent)\"", "medium"),
    ("passwd", "medium"),
    ("sudo hostnamectl set-hostname box", "medium"),
    ("chmod 777 file.txt", "medium"),
    # info leak
    ("env", "info_leak"),
    ("printenv | grep PATH", "info_leak"),
    ("echo $GITHUB_TOKEN", "info_leak"),
    # safe (several of these were false positives before)
    ("ls -la", "safe"),
    ("python3 -m venv venv", "safe"),
    ("reset", "safe"),
    ("hostname -I", "safe"),
    ("git add .", "safe"),
    ("echo 'hello world'", "safe"),
])
def test_risk_level(command, status):
    assert check_command_safety(command)["status"] == status
