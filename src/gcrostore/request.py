import enum

from gcrostore import api_version, app, config, mail, models

code_to_platform = {platform.code: platform for platform in config.platforms}
PlatformCode = enum.Enum(  # type: ignore
    "PlatformCode", {key: key for key in code_to_platform.keys()}
)  # TODO: Is there a more smart way to create Enum from iterables?


@app.post(f"/{api_version}/request/login")  # TODO: Add tags
def request_login(
    user: models.User,
    selenium: models.Selenium,
    platform_code: PlatformCode | None = None,
) -> None:
    platforms = (
        config.platforms.copy()
        if platform_code is None
        else [code_to_platform[platform_code.value]]
    )
    for platform in platforms:
        with selenium.driver() as driver:
            if not platform.is_accessible_to_userpage(driver):
                mail.request_relogin(user, platform, selenium)
