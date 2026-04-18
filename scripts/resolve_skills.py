import yaml, os, subprocess, shutil, sys

agent_dir = sys.argv[1]
agent_file = os.path.join(agent_dir, "agent.yaml")

with open(agent_file) as f:
    data = yaml.safe_load(f)

skills = data.get("skills", [])
new_skills = []

os.makedirs("tmp", exist_ok=True)
os.makedirs(os.path.join(agent_dir, "skills"), exist_ok=True)

for skill in skills:
    if isinstance(skill, str) and skill.startswith("github.com"):
        print(f"Resolving {skill}")

        parts = skill.split("/")
        org = parts[1]
        repo = parts[2]
        branch = parts[4]
        subpath = "/".join(parts[5:])

        skill_name = os.path.basename(subpath)

        clone_dir = f"tmp/{repo}"

        if not os.path.exists(clone_dir):
            subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", branch,
                 f"https://github.com/{org}/{repo}.git", clone_dir],
                check=True
            )

        source_path = os.path.join(clone_dir, subpath)
        target_path = os.path.join(agent_dir, "skills", skill_name)

        if os.path.exists(target_path):
            shutil.rmtree(target_path)

        shutil.copytree(source_path, target_path)

        # CRITICAL: replace reference
        new_skills.append(skill_name)

    else:
        new_skills.append(skill)

# rewrite agent.yaml
data["skills"] = new_skills

with open(agent_file, "w") as f:
    yaml.dump(data, f)

print("✅ agent.yaml rewritten with local skill names")