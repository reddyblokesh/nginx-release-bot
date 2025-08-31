import subprocess
import os
import shutil
import logging
import sys
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def pull_chart(chart_version, tag):
    # Always use the project root's charts/nginx-release-charts directory
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "charts", "nginx-release-charts")
    try:
        os.makedirs(output_dir, exist_ok=True)
        subprocess.run([
            "helm", "pull",
            "oci://ghcr.io/nginx/charts/nginx-ingress",
            "--untar",
            "--version", chart_version,
            "--destination", output_dir
        ], check=True)
        src = os.path.join(output_dir, "nginx-ingress")
        dst = os.path.join(output_dir, f"nginx-oss-{tag}")
        if os.path.exists(dst):
            shutil.rmtree(dst)
        os.rename(src, dst)
        logging.info(f"Chart pulled and renamed to {dst}")
        return dst
    except subprocess.CalledProcessError as e:
        logging.error(f"Helm pull failed: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Failed to move or rename chart directory: {e}")
        sys.exit(1)

def selective_replace_chart_files(new_chart_dir, old_chart_dir=None):
    if old_chart_dir is None:
        old_chart_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "charts", "ml-nginx-ingress")
    items_to_replace = [
        "templates",
        ".helmignore",
        "Chart.yaml",
        "README.md",
        "values-icp.yaml",
        "values-nsm.yaml",
        "values-plus.yaml",
        "values.yaml"
    ]
    for item in items_to_replace:
        old_item_path = os.path.join(old_chart_dir, item)
        new_item_path = os.path.join(new_chart_dir, item)
        try:
            if os.path.exists(old_item_path):
                if os.path.isdir(old_item_path):
                    shutil.rmtree(old_item_path)
                else:
                    os.remove(old_item_path)
                logging.info(f"Removed old {item} from {old_chart_dir}")
            if os.path.exists(new_item_path):
                if os.path.isdir(new_item_path):
                    shutil.copytree(new_item_path, old_item_path)
                else:
                    shutil.copy2(new_item_path, old_item_path)
                logging.info(f"Copied new {item} to {old_chart_dir}")
            else:
                logging.warning(f"{item} not found in new chart directory; skipping.")
        except Exception as e:
            logging.error(f"Error replacing {item}: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nic-version", type=str, default="", help="Override NIC version")
    parser.add_argument("--chart-version", type=str, default="", help="Override Chart version")
    args = parser.parse_args()

    release_nic_version = args.nic_version.strip()
    chart_version = args.chart_version.strip()

    release_url = "https://docs.nginx.com/nginx-ingress-controller/releases"

    if not release_nic_version and not chart_version:
        # Prompt for both
        release_nic_version = input(
            f"Enter the NIC version (e.g., 5.1.1).\nYou can find the latest NIC version here: {release_url}\n"
        ).strip()
        if not release_nic_version:
            logging.error(f"NIC version is required. See: {release_url}")
            sys.exit(1)
        chart_version = input("Enter the Helm chart version (e.g., 2.2.2): ").strip()
        if not chart_version:
            print(f"You can find the latest Helm chart version here: {release_url}")
            logging.error("Helm chart version is required.")
            sys.exit(1)
    elif release_nic_version and not chart_version:
        chart_version = input("Enter the Helm chart version (e.g., 2.2.2): ").strip()
        if not chart_version:
            print(f"You can find the latest Helm chart version here: {release_url}")
            logging.error("Helm chart version is required.")
            sys.exit(1)
    elif chart_version and not release_nic_version:
        release_nic_version = input(
            f"Enter the NIC version (e.g., 5.1.1).\nYou can find the latest NIC version here: {release_url}: \n"
        ).strip()
        if not release_nic_version:
            logging.error(f"NIC version is required. See: {release_url}")
            sys.exit(1)

    if not release_nic_version or not chart_version:
        logging.error("Both NIC version and Chart version are required.")
        sys.exit(1)
    logging.info(f"Using NIC version: {release_nic_version} and Chart version: {chart_version}")

    new_chart_dir = pull_chart(chart_version, release_nic_version)
    selective_replace_chart_files(new_chart_dir)
    logging.info("NGINX chart update completed successfully.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)
