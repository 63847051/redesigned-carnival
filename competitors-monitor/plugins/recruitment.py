#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招聘流程自动化插件
简历解析、候选人筛选、面试安排、邮件通知
"""

import json
import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Any


class ResumeParser:
    """简历解析器"""

    def __init__(self):
        pass

    def parse(self, file_path: str) -> Dict:
        """解析简历文件"""
        if not os.path.exists(file_path):
            return {"error": f"文件不存在: {file_path}"}

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".txt":
            return self._parse_txt(file_path)
        elif ext == ".pdf":
            return self._parse_pdf(file_path)
        elif ext == ".docx":
            return self._parse_docx(file_path)
        else:
            return {"error": f"不支持的文件格式: {ext}"}

    def _parse_txt(self, file_path: str) -> Dict:
        """解析文本简历"""
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        return self._extract_info(text)

    def _parse_pdf(self, file_path: str) -> Dict:
        """解析 PDF 简历"""
        try:
            import PyPDF2

            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
            return self._extract_info(text)
        except ImportError:
            return {"error": "需要安装 PyPDF2"}

    def _parse_docx(self, file_path: str) -> Dict:
        """解析 DOCX 简历"""
        try:
            import docx

            doc = docx.Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
            return self._extract_info(text)
        except ImportError:
            return {"error": "需要安装 python-docx"}

    def _extract_info(self, text: str) -> Dict:
        """从文本提取信息"""
        info = {
            "raw_text": text[:1000],
            "name": "",
            "email": "",
            "phone": "",
            "education": "",
            "experience_years": 0,
            "skills": [],
        }

        name_match = re.search(r"^([^\n]+)", text)
        if name_match:
            info["name"] = name_match.group(1).strip()

        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        if email_match:
            info["email"] = email_match.group()

        phone_match = re.search(r"1[3-9]\d{9}", text)
        if phone_match:
            info["phone"] = phone_match.group()

        education_keywords = ["博士", "硕士", "本科", "大专", "高中"]
        for edu in education_keywords:
            if edu in text:
                info["education"] = edu
                break

        exp_matches = re.findall(r"(\d+)\s*(年|years)", text)
        if exp_matches:
            info["experience_years"] = max([int(m[0]) for m in exp_matches])

        skill_keywords = [
            "Python",
            "Java",
            "JavaScript",
            "C++",
            "Go",
            "Rust",
            "Django",
            "Flask",
            "Spring",
            "React",
            "Vue",
            "Angular",
            "MySQL",
            "PostgreSQL",
            "MongoDB",
            "Redis",
            "AWS",
            "Azure",
            "GCP",
            "Docker",
            "Kubernetes",
            "SQL",
            "Excel",
            "Tableau",
            "机器学习",
            "深度学习",
        ]

        for skill in skill_keywords:
            if skill.lower() in text.lower():
                info["skills"].append(skill)

        return info


class CandidateScreener:
    """候选人筛选器"""

    def __init__(self, config: Dict):
        self.config = config

    def screen(self, resume_info: Dict) -> List[Dict]:
        """筛选候选人"""
        results = []

        for position in self.config.get("positions", []):
            match_result = self._calculate_match(resume_info, position)
            if match_result["score"] >= self.config.get("check_rules", {}).get(
                "match_score_threshold", 0.6
            ):
                results.append(match_result)

        return results

    def _calculate_match(self, resume: Dict, position: Dict) -> Dict:
        """计算匹配度"""
        requirements = position.get("requirements", {})
        keywords = position.get("keywords", [])
        weights = position.get(
            "weight", {"skills": 0.5, "experience": 0.3, "education": 0.2}
        )

        resume_skills = [s.lower() for s in resume.get("skills", [])]
        required_skills = [s.lower() for s in requirements.get("skills", [])]

        skills_match = 0
        for skill in required_skills:
            if any(skill in rs for rs in resume_skills):
                skills_match += 1

        skills_score = skills_match / len(required_skills) if required_skills else 0

        resume_exp = resume.get("experience_years", 0)
        required_exp = requirements.get("experience_years_min", 0)
        exp_score = min(resume_exp / required_exp, 1.0) if required_exp else 1.0

        edu_levels = {"高中": 1, "大专": 2, "本科": 3, "硕士": 4, "博士": 5}
        resume_edu = edu_levels.get(resume.get("education", ""), 0)
        required_edu = edu_levels.get(requirements.get("education", "本科"), 3)
        edu_score = 1.0 if resume_edu >= required_edu else 0.5

        total_score = (
            skills_score * weights.get("skills", 0.5)
            + exp_score * weights.get("experience", 0.3)
            + edu_score * weights.get("education", 0.2)
        )

        return {
            "position_id": position.get("id"),
            "position_title": position.get("title"),
            "score": round(total_score, 2),
            "skills_match": skills_score,
            "experience_match": exp_score,
            "education_match": edu_score,
            "matched_skills": [s for s in required_skills if s in resume_skills],
            "missing_skills": [s for s in required_skills if s not in resume_skills],
        }


class EmailNotifier:
    """邮件通知"""

    def __init__(self, config: Dict):
        self.config = config

    def send(self, to: str, subject: str, body: str) -> bool:
        """发送邮件"""
        email_config = self.config.get("data_sources", {}).get("email", {})

        if not email_config.get("enabled"):
            print(f"[模拟发送邮件] To: {to}, Subject: {subject}")
            return True

        smtp_server = email_config.get("smtp_server")
        smtp_port = email_config.get("smtp_port", 587)
        sender = email_config.get("sender_email")
        password = email_config.get("sender_password")

        if not all([smtp_server, sender, password]):
            return False

        try:
            msg = MIMEMultipart()
            msg["From"] = sender
            msg["To"] = to
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain", "utf-8"))

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
            server.quit()

            return True
        except Exception as e:
            print(f"发送邮件失败: {e}")
            return False


class RecruitmentAutomation:
    """招聘流程自动化"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.parser = ResumeParser()
        self.screener = CandidateScreener(config)
        self.notifier = EmailNotifier(config)
        self.candidates_file = "data/candidates.json"
        self.candidates = self._load_candidates()

    def run(self) -> Dict:
        """运行招聘流程"""
        results = {"new_resumes": [], "candidates": [], "alerts": []}

        resume_folder = self.config.get("data_sources", {}).get("resume_folder", "")

        if os.path.exists(resume_folder):
            for filename in os.listdir(resume_folder):
                if filename.endswith((".txt", ".pdf", ".docx")):
                    path = os.path.join(resume_folder, filename)
                    resume_info = self.parser.parse(path)

                    if "error" not in resume_info:
                        matches = self.screener.screen(resume_info)

                        candidate = {
                            "name": resume_info.get("name", filename),
                            "email": resume_info.get("email", ""),
                            "phone": resume_info.get("phone", ""),
                            "resume_file": filename,
                            "matches": matches,
                            "stage": "新简历",
                            "added_at": datetime.now().isoformat(),
                        }

                        results["new_resumes"].append(candidate)

        if not results["new_resumes"]:
            results["candidates"] = self._generate_mock_candidates()

        for candidate in results["candidates"]:
            if candidate.get("matches"):
                results["alerts"].append(
                    {
                        "type": "new_candidate",
                        "severity": "info",
                        "candidate": candidate.get("name"),
                        "best_match": candidate["matches"][0]["position_title"],
                        "score": candidate["matches"][0]["score"],
                        "message": f"新候选人: {candidate.get('name')} (匹配: {candidate['matches'][0]['position_title']})",
                    }
                )

        self._save_candidates(results["candidates"])

        return results

    def _load_candidates(self) -> List[Dict]:
        """加载候选人数据"""
        if os.path.exists(self.candidates_file):
            with open(self.candidates_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_candidates(self, candidates: List[Dict]):
        """保存候选人数据"""
        os.makedirs("data", exist_ok=True)
        with open(self.candidates_file, "w", encoding="utf-8") as f:
            json.dump(candidates, f, ensure_ascii=False, indent=2)

    def _generate_mock_candidates(self) -> List[Dict]:
        """生成模拟候选人数据"""
        return [
            {
                "name": "张三",
                "email": "zhangsan@example.com",
                "phone": "13800138000",
                "matches": [
                    {
                        "position_id": "python_dev",
                        "position_title": "Python 开发工程师",
                        "score": 0.85,
                        "matched_skills": ["Python", "Django", "PostgreSQL"],
                        "missing_skills": ["Redis"],
                    }
                ],
                "stage": "一面",
                "added_at": datetime.now().isoformat(),
            },
            {
                "name": "李四",
                "email": "lisi@example.com",
                "phone": "13900139000",
                "matches": [
                    {
                        "position_id": "data_analyst",
                        "position_title": "数据分析师",
                        "score": 0.72,
                        "matched_skills": ["Python", "SQL", "Excel"],
                        "missing_skills": ["Tableau"],
                    }
                ],
                "stage": "筛选",
                "added_at": datetime.now().isoformat(),
            },
        ]

    def generate_report(self, results: Dict) -> str:
        """生成招聘报告"""
        report = "## 📋 招聘流程报告\n\n"

        report += f"**日期**: {datetime.now().strftime('%Y-%m-%d')}\n\n"

        candidates = results.get("candidates", [])
        report += f"**候选人总数**: {len(candidates)}\n\n"

        stages = {}
        for c in candidates:
            stage = c.get("stage", "未知")
            stages[stage] = stages.get(stage, 0) + 1

        report += "### 各阶段人数\n\n"
        for stage, count in stages.items():
            report += f"- {stage}: {count} 人\n"
        report += "\n"

        report += "### 候选人详情\n\n"

        for c in candidates:
            name = c.get("name", "未知")
            stage = c.get("stage", "未知")
            matches = c.get("matches", [])

            report += f"**{name}** - {stage}\n\n"

            for m in matches:
                report += f"- 匹配职位: {m.get('position_title')} (匹配度: {m.get('score') * 100:.0f}%)\n"

            report += "\n"

        alerts = results.get("alerts", [])
        if alerts:
            report += "### ⚠️ 告警\n\n"
            for alert in alerts:
                report += f"- {alert.get('message')}\n"

        return report


def run_recruitment():
    """运行招聘流程"""
    import sys

    config_path = "config/recruitment.json"

    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    recruitment = RecruitmentAutomation(config)
    results = recruitment.run()

    print(f"处理了 {len(results.get('new_resumes', []))} 份新简历")
    print(f"候选人数: {len(results.get('candidates', []))}")
    print(f"告警数: {len(results.get('alerts', []))}")

    report = recruitment.generate_report(results)
    print("\n" + report)

    return results


if __name__ == "__main__":
    run_recruitment()
