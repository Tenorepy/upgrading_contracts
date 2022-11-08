from scripts.helpful_scripts import get_account, encode_function_data, upgrade
from brownie import (
    config,
    network,
    Box,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    BoxV2,
    Contract,
)


def main():
    account = get_account()
    print(f"Deploying to {network.show_active()}")
    box = Box.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )

    proxy_admin = ProxyAdmin.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )

    # initializer = box.store, 1
    box_encoded_initializer_function = encode_function_data()
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
        publish_source=config["networks"][network.show_active()]["verify"],
    )
    print(f"Proxy deployed to {proxy}. You can now upgrade to V2!")
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    proxy_box.store(
        1,
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )

    # upgrade
    box_v2 = BoxV2.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )
    upgrade_transaction = upgrade(
        account,
        proxy,
        box_v2.address,
        proxy_admin_contract=proxy_admin,
    )
    upgrade_transaction.wait(1)
    print("Proxy has been updated!")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    proxy_box.increment(
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )
    print(proxy_box.retrieve())
