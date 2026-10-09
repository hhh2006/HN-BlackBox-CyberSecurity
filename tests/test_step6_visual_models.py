from core.cryptography.visualization import visual_models


def test_visual_model_helpers_are_presentation_only():
    assert visual_models._hex_bytes("HN", 4) == ["48", "4E", "00", "00"]
    assert callable(visual_models.draw_aes_state_hud)
    assert callable(visual_models.draw_rsa_flow_hud)
    assert callable(visual_models.draw_hash_hud)
    assert callable(visual_models.draw_stego_hud)
