"""The browser must send the same mode defaults as the provider."""
import json
import subprocess
from pathlib import Path
import pytest
from mq_image_analyze.vision.semantic.provider import default_model_for_mode

HTML = Path(__file__).resolve().parents[1] / 'mq_image_analyze/web/index.html'

@pytest.mark.parametrize('mode', ['local-fast', 'local-deep', 'cloud-verify'])
@pytest.mark.parametrize('previous', ['', 'qwen3.5:9b'])
def test_browser_model_on_mode_change(mode, previous):
    source = HTML.read_text().split("visionMode.addEventListener('change', () => {", 1)[1].split('\n});', 1)[0]
    script = ('const visionMode = {value: ' + json.dumps(mode) + '};'
              'const visionModel = {value: ' + json.dumps(previous) + '};' + source +
              ';console.log(JSON.stringify(visionModel));')
    result = subprocess.run(['node', '-e', script], capture_output=True, text=True, check=True)
    assert json.loads(result.stdout)['value'] == default_model_for_mode(mode)
