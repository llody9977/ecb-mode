from ecb_lab.cut_and_paste import ProfileService, forge_admin_token


def test_normal_token_is_role_user():
    service = ProfileService()
    token = service.issue_token("alice@example.com")
    assert service.role_for_token(token) == "user"


def test_forged_token_decrypts_to_role_admin_without_the_key():
    service = ProfileService()
    forged = forge_admin_token(service)
    assert service.role_for_token(forged) == "admin"


def test_forgery_uses_only_the_public_interface():
    # Sanity check that the exploit never touches service.key directly (AST-based, so it
    # can't be fooled by the word "key" appearing in a comment or docstring).
    import ast
    import inspect

    from ecb_lab import cut_and_paste

    tree = ast.parse(inspect.getsource(cut_and_paste.forge_admin_token))
    key_accesses = [
        node.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute) and node.attr == "key"
    ]
    assert key_accesses == []
