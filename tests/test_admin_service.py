from services.domain.admin_service import AdminService


def test_register_auto_activates_new_model():
    service = AdminService()

    register_resp = service.handle(
        {
            "action": "register",
            "modelId": "new-model",
            "provider": "mock",
        }
    )

    assert register_resp["model"]["modelId"] == "new-model"
    active = service.handle({"action": "active"})
    assert active["modelId"] == "new-model"


def test_register_can_skip_activation():
    service = AdminService()
    service.handle({"action": "register", "modelId": "first"})
    service.handle({"action": "activate", "modelId": "first"})

    service.handle(
        {
            "action": "register",
            "modelId": "second",
            "activate": False,
        }
    )

    active = service.handle({"action": "active"})
    assert active["modelId"] == "first"
