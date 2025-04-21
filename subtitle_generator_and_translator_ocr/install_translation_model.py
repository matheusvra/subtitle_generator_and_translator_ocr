import argostranslate.package
import argostranslate.translate
from loguru import logger


def install_translation_model_if_needed(from_code="en", to_code="pt"):
    logger.info(
        f"Verificando se o modelo de tradução {from_code} → {to_code} está instalado..."
    )

    installed_languages = argostranslate.translate.get_installed_languages()
    from_lang = next(
        (lang for lang in installed_languages if lang.code == from_code), None
    )
    to_lang = next((lang for lang in installed_languages if lang.code == to_code), None)

    if from_lang and to_lang and from_lang.get_translation(to_lang):
        logger.info("Modelo já instalado.")
        return

    logger.info(
        f"Baixando e instalando o modelo de tradução {from_code} → {to_code}..."
    )

    try:
        # Atualiza o índice de pacotes disponíveis
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        
        # Log available packages for debugging purposes
        logger.info("Pacotes de tradução disponíveis:")
        for pkg in available_packages:
            logger.info(f"De: {pkg.from_code}, Para: {pkg.to_code}")

        # Encontra o pacote de tradução desejado
        package_to_install = next(
            (
                pkg
                for pkg in available_packages
                if pkg.from_code == from_code and pkg.to_code == to_code
            ),
            None,
        )

        if package_to_install is None:
            logger.error(f"Modelo de tradução {from_code} → {to_code} não encontrado.")
            raise RuntimeError("Modelo de tradução não disponível.")

        # Baixa e instala o pacote
        download_path = package_to_install.download()
        argostranslate.package.install_from_path(download_path)
        logger.info("Modelo instalado com sucesso.")

    except Exception as e:
        logger.error(f"Erro ao baixar ou instalar o modelo: {e}")
        raise RuntimeError("Falha ao instalar o modelo de tradução.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 3:
        from_code = sys.argv[1]
        to_code = sys.argv[2]
    else:
        from_code = "en"
        to_code = "pt-br"

    install_translation_model_if_needed(from_code, to_code)
