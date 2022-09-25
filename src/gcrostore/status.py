import enum

from gcrostore import api_version, app, config, mail, models

code_to_platform = {platform.code: platform for platform in config.platforms}
PlatformCode = enum.Enum(  # type: ignore
    "PlatformCode", {key: key for key in code_to_platform.keys()}
)  # TODO: Is there a more smart way to create Enum from iterables?


@app.post(f"/{api_version}/status/login")
def check_login_status(
    user: models.User,
    platform_code: PlatformCode,
    selenium: models.Selenium,
) -> bool:
    platform = code_to_platform[platform_code.value]
    with selenium.driver() as driver:
        if not platform.is_accessible_to_userpage(driver):
            mail.request_relogin(user, platform, selenium)
            return False
    return True
