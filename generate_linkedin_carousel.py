import os
from PIL import Image, ImageDraw, ImageFont

def create_carousel():
    base_dir = r"C:\ag-prg\ai-code-reviewer"
    output_pdf = os.path.join(base_dir, "LinkedIn_Carousel_AI_Code_Reviewer.pdf")
    output_slides_dir = os.path.join(base_dir, "carousel_slides")
    os.makedirs(output_slides_dir, exist_ok=True)

    W, H = 1080, 1080
    font_dir = r"C:\Windows\Fonts"

    f_hero = ImageFont.truetype(os.path.join(font_dir, "segoeuib.ttf"), 46)
    f_title = ImageFont.truetype(os.path.join(font_dir, "segoeuib.ttf"), 30)
    f_card_title = ImageFont.truetype(os.path.join(font_dir, "segoeuib.ttf"), 20)
    f_sub = ImageFont.truetype(os.path.join(font_dir, "segoeui.ttf"), 17)
    f_badge = ImageFont.truetype(os.path.join(font_dir, "segoeuib.ttf"), 13)
    f_pill = ImageFont.truetype(os.path.join(font_dir, "segoeuib.ttf"), 15)
    f_pill_sub = ImageFont.truetype(os.path.join(font_dir, "segoeui.ttf"), 12)
    f_footer = ImageFont.truetype(os.path.join(font_dir, "segoeui.ttf"), 13)
    f_body = ImageFont.truetype(os.path.join(font_dir, "segoeui.ttf"), 15)
    f_mono = ImageFont.truetype(os.path.join(font_dir, "consola.ttf"), 14)
    f_mono_sm = ImageFont.truetype(os.path.join(font_dir, "consola.ttf"), 12)

    slides = []

    # ==========================================
    # SLIDE 1: COVER SLIDE
    # ==========================================
    s1 = Image.new("RGB", (W, H), (11, 17, 32))
    d1 = ImageDraw.Draw(s1)
    d1.rectangle((0, 0, W, 8), fill=(59, 130, 246))

    d1.rounded_rectangle((60, 60, 430, 96), radius=8, fill=(30, 41, 59), outline=(51, 65, 85))
    d1.text((75, 70), "🤖 AI ENGINEERING PORTFOLIO • PROJECT 4", fill=(56, 189, 248), font=f_badge)
    d1.text((W - 160, 70), "Slide 1 of 8", fill=(148, 163, 184), font=f_badge)

    d1.text((60, 130), "AI Code Review Bot &\nAutomated Security Auditor", fill=(248, 250, 252), font=f_hero, spacing=10)
    d1.text((60, 250), "Zero-Day & Secret Scanner, Unified Diff Analyzer, and 1-Click GitHub Suggestions", fill=(148, 163, 184), font=f_sub)

    cards = [
        ("🛡️ OWASP Top 10 & Secret Scanner", "Catches AWS keys, OpenAI tokens, SQL injection, RCE (eval), and insecure deserialization.", (239, 68, 68)),
        ("🧠 Multi-Pass AI Review Engine", "Dual-pass hybrid pipeline pairing static regex heuristics with Gemini 2.0 Flash reasoning.", (168, 85, 247)),
        ("💡 1-Click Inline Fix Suggestions", "Generates standardized GitHub ```suggestion diff blocks ready for instant merge.", (34, 197, 94)),
        ("📊 0–100 Health Score & Verdicts", "Objective PR quality scoring: APPROVE (≥80), COMMENT (60-79), or REQUEST_CHANGES (<60).", (59, 130, 246)),
    ]

    card_w, card_h = 460, 160
    positions = [(60, 310), (560, 310), (60, 490), (560, 490)]

    for (c_title, c_desc, c_accent), (cx, cy) in zip(cards, positions):
        d1.rounded_rectangle((cx, cy, cx + card_w, cy + card_h), radius=14, fill=(15, 23, 42), outline=(51, 65, 85), width=2)
        d1.rectangle((cx + 14, cy + 18, cx + 18, cy + 44), fill=c_accent)
        d1.text((cx + 28, cy + 20), c_title, fill=(248, 250, 252), font=f_card_title)
        
        words = c_desc.split()
        lines = []
        curr = ""
        for w in words:
            test = curr + " " + w if curr else w
            if len(test) > 42:
                lines.append(curr)
                curr = w
            else:
                curr = test
        if curr:
            lines.append(curr)
        d1.text((cx + 28, cy + 62), "\n".join(lines), fill=(148, 163, 184), font=f_sub, spacing=6)

    d1.rounded_rectangle((60, 680, W - 60, 830), radius=16, fill=(17, 24, 39), outline=(59, 130, 246), width=2)
    d1.text((90, 706), "🎯 HOW MODERN ENGINEERING TEAMS SCALE AUTOMATED CODE QUALITY", fill=(96, 165, 250), font=f_badge)
    d1.text((90, 736), "Swipe through to see how Unified Diff parsing, deterministic OWASP scanning,\nGemini 2.0 Flash reasoning, and GitHub REST webhooks eliminate PR review bottlenecks.", fill=(226, 232, 240), font=f_sub, spacing=6)
    d1.text((90, 794), "FastAPI • Gemini 2.0 Flash • Unidiff • GitHub REST API • Tailwind CSS • Docker", fill=(148, 163, 184), font=f_footer)

    d1.line((60, H - 90, W - 60, H - 90), fill=(30, 41, 59), width=1)
    d1.text((60, H - 65), "Source Code: github.com/jayshreeganesh/ai-code-reviewer", fill=(100, 116, 139), font=f_footer)
    d1.text((W - 270, H - 65), "Swipe for Pipeline →", fill=(56, 189, 248), font=f_pill)

    s1.save(os.path.join(output_slides_dir, "slide_1.png"))
    slides.append(s1)

    # ==========================================
    # SLIDE 2: THE CHALLENGE
    # ==========================================
    s2 = Image.new("RGB", (W, H), (11, 17, 32))
    d2 = ImageDraw.Draw(s2)
    d2.rounded_rectangle((60, 50, 270, 80), radius=6, fill=(30, 41, 59), outline=(51, 65, 85))
    d2.text((75, 57), "PILLAR 01: THE CHALLENGE", fill=(56, 189, 248), font=f_badge)
    d2.text((W - 160, 57), "Slide 2 of 8", fill=(148, 163, 184), font=f_badge)

    d2.text((60, 100), "Why Manual Code Reviews Fail Under Pressure", fill=(248, 250, 252), font=f_title)
    d2.text((60, 142), "Modern CI/CD pipelines move fast, but peer code review remains a major security vulnerability.", fill=(148, 163, 184), font=f_sub)

    # Comparison Columns
    d2.rounded_rectangle((60, 200, 520, 760), radius=14, fill=(15, 23, 42), outline=(239, 68, 68), width=2)
    d2.text((85, 225), "❌ Traditional Manual PR Reviews", fill=(244, 63, 94), font=f_card_title)
    d2.text((85, 265), "Pain points that slow teams & leak bugs:", fill=(148, 163, 184), font=f_sub)
    bad_items = [
        "Reviewer Fatigue: Overlooking subtle SQL injections & unescaped strings in 500+ line diffs",
        "Accidental Secret Leaks: Hardcoded AWS / OpenAI keys slip into git commit histories",
        "Subjective Nitpicking: Wasting senior engineering time debating style instead of architecture",
        "Turnaround Lag: PRs sit idle for 2-3 days waiting for reviewer availability, killing velocity"
    ]
    for idx, item in enumerate(bad_items):
        iy = 310 + idx * 105
        d2.rounded_rectangle((85, iy, 495, iy + 85), radius=8, fill=(30, 41, 59))
        d2.text((100, iy + 14), f"• {item[:38]}", fill=(254, 202, 202), font=f_pill)
        d2.text((100, iy + 42), item[38:], fill=(203, 213, 225), font=f_pill_sub)

    d2.rounded_rectangle((560, 200, 1020, 760), radius=14, fill=(15, 23, 42), outline=(34, 197, 94), width=2)
    d2.text((585, 225), "✅ Automated AI Code Review Bot", fill=(74, 222, 128), font=f_card_title)
    d2.text((585, 265), "Automated guardrails before merging:", fill=(148, 163, 184), font=f_sub)
    good_items = [
        "Instant OWASP Audit: Zero false negatives on critical API keys, SQLi, and unsafe eval() calls",
        "Context-Aware Reasoning: Gemini 2.0 Flash spots resource leaks and anti-patterns across hunks",
        "Actionable 1-Click Fixes: Line-by-line diff replacements developers can commit instantly",
        "Merge Gate Verdicts: Automatically blocks merging if Health Score falls below threshold"
    ]
    for idx, item in enumerate(good_items):
        iy = 310 + idx * 105
        d2.rounded_rectangle((585, iy, 995, iy + 85), radius=8, fill=(30, 41, 59))
        d2.text((600, iy + 14), f"✓ {item[:38]}", fill=(187, 247, 208), font=f_pill)
        d2.text((600, iy + 42), item[38:], fill=(203, 213, 225), font=f_pill_sub)

    d2.line((60, H - 90, W - 60, H - 90), fill=(30, 41, 59), width=1)
    d2.text((60, H - 65), "Eliminating security vulnerabilities before code touches production.", fill=(100, 116, 139), font=f_footer)
    d2.text((W - 270, H - 65), "Next: Security Engine →", fill=(56, 189, 248), font=f_pill)
    s2.save(os.path.join(output_slides_dir, "slide_2.png"))
    slides.append(s2)

    # ==========================================
    # SLIDE 3: OWASP & SECRET SCANNER
    # ==========================================
    s3 = Image.new("RGB", (W, H), (11, 17, 32))
    d3 = ImageDraw.Draw(s3)
    d3.rounded_rectangle((60, 50, 280, 80), radius=6, fill=(30, 41, 59), outline=(51, 65, 85))
    d3.text((75, 57), "PILLAR 02: SECURITY ENGINE", fill=(56, 189, 248), font=f_badge)
    d3.text((W - 160, 57), "Slide 3 of 8", fill=(148, 163, 184), font=f_badge)

    d3.text((60, 100), "Deterministic OWASP Top 10 & Secret Scanner", fill=(248, 250, 252), font=f_title)
    d3.text((60, 142), "Sub-millisecond pattern matching designed to catch high-severity vulnerabilities without LLM latency.", fill=(148, 163, 184), font=f_sub)

    sec_cards = [
        ("🔑 Hardcoded Secrets & API Keys", "Matches AWS Keys (AKIA...), GitHub tokens (ghp_...), OpenAI keys (sk-...), and RSA/EC private keys.", 'AWS_KEY = "AKIA1234567890ABCDEF"', (239, 68, 68)),
        ("💉 SQL Injection (CWE-89)", "Detects unescaped string interpolation and f-strings inside raw SQL statements.", 'query = f"SELECT * FROM secrets WHERE id = \'{user_id}\'"', (249, 115, 22)),
        ("⚡ Arbitrary Code Execution (CWE-95/94)", "Catches unsafe eval(), exec(), and subprocess invocations with shell=True enabled.", 'eval(user_supplied_expression)', (239, 68, 68)),
        ("📦 Insecure Deserialization (CWE-502)", "Identifies dangerous pickle.loads() and PyYAML load() calls without SafeLoader.", 'data = pickle.loads(untrusted_payload)', (245, 158, 11)),
    ]

    for idx, (stitle, sdesc, scode, scolor) in enumerate(sec_cards):
        cy = 195 + idx * 145
        d3.rounded_rectangle((60, cy, W - 60, cy + 130), radius=12, fill=(15, 23, 42), outline=(51, 65, 85), width=2)
        d3.rectangle((74, cy + 14, 78, cy + 42), fill=scolor)
        d3.text((90, cy + 16), stitle, fill=(248, 250, 252), font=f_card_title)
        d3.text((90, cy + 48), sdesc, fill=(148, 163, 184), font=f_sub)
        d3.rounded_rectangle((90, cy + 80, W - 90, cy + 116), radius=6, fill=(30, 41, 59))
        d3.text((105, cy + 90), f"⚠ Trigger: {scode}", fill=(248, 113, 113), font=f_mono_sm)

    d3.rounded_rectangle((60, 790, W - 60, 860), radius=10, fill=(17, 24, 39), outline=(34, 197, 94))
    d3.text((85, 805), "🛡️ ZERO TOLERANCE SECURITY POLICY", fill=(74, 222, 128), font=f_badge)
    d3.text((85, 830), "Any critical secret leak or OWASP finding triggers an immediate REQUEST_CHANGES verdict.", fill=(226, 232, 240), font=f_sub)

    d3.line((60, H - 90, W - 60, H - 90), fill=(30, 41, 59), width=1)
    d3.text((60, H - 65), "Static analysis executes in <5ms per hunk before invoking AI reasoning.", fill=(100, 116, 139), font=f_footer)
    d3.text((W - 270, H - 65), "Next: 1-Click Fixes →", fill=(56, 189, 248), font=f_pill)
    s3.save(os.path.join(output_slides_dir, "slide_3.png"))
    slides.append(s3)

    # ==========================================
    # SLIDE 4: 1-CLICK GITHUB INLINE FIXES
    # ==========================================
    s4 = Image.new("RGB", (W, H), (11, 17, 32))
    d4 = ImageDraw.Draw(s4)
    d4.rounded_rectangle((60, 50, 310, 80), radius=6, fill=(30, 41, 59), outline=(51, 65, 85))
    d4.text((75, 57), "PILLAR 03: DEVELOPER FIXES", fill=(56, 189, 248), font=f_badge)
    d4.text((W - 160, 57), "Slide 4 of 8", fill=(148, 163, 184), font=f_badge)

    d4.text((60, 100), "1-Click GitHub Inline Fix Suggestions", fill=(248, 250, 252), font=f_title)
    d4.text((60, 142), "Don't just point out bugs—generate ready-to-merge GitHub diff replacement suggestions.", fill=(148, 163, 184), font=f_sub)

    # Mock GitHub Review Box
    d4.rounded_rectangle((60, 200, W - 60, 770), radius=14, fill=(15, 23, 42), outline=(51, 65, 85), width=2)
    
    # Header bar
    d4.rounded_rectangle((60, 200, W - 60, 260), radius=14, fill=(30, 41, 59))
    d4.text((85, 218), "ai-code-reviewer-bot", fill=(248, 250, 252), font=f_card_title)
    d4.rounded_rectangle((280, 218, 335, 244), radius=6, fill=(239, 68, 68))
    d4.text((290, 224), "BOT", fill=(255, 255, 255), font=f_badge)
    d4.text((350, 222), "commented on services/auth.py (Line 16)", fill=(148, 163, 184), font=f_sub)

    # Body
    d4.text((85, 280), "🚨 Critical Security Vulnerability: SQL Injection (Formatted Query)", fill=(248, 113, 113), font=f_card_title)
    d4.text((85, 315), "User input is directly concatenated into the SQL statement via an f-string, allowing SQL injection.", fill=(203, 213, 225), font=f_sub)
    d4.text((85, 345), "Suggested remediation using parameterized queries:", fill=(148, 163, 184), font=f_sub)

    # Diff Box
    d4.rounded_rectangle((85, 385, W - 85, 630), radius=10, fill=(11, 17, 32), outline=(51, 65, 85))
    
    # Original Red line
    d4.rectangle((85, 400, W - 85, 455), fill=(69, 10, 10))
    d4.text((105, 415), "- 16   query = f\"SELECT * FROM secrets WHERE id = '{user_id}'\"", fill=(248, 113, 113), font=f_mono)

    # Replacement Green line
    d4.rectangle((85, 465, W - 85, 545), fill=(6, 78, 59))
    d4.text((105, 480), "+ 16   # Parameterized query to prevent SQL injection", fill=(110, 231, 183), font=f_mono)
    d4.text((105, 510), "+ 17   cursor.execute(\"SELECT * FROM secrets WHERE id = %s\", (user_id,))", fill=(110, 231, 183), font=f_mono)

    # Commit Suggestion Button
    d4.rounded_rectangle((85, 570, 310, 615), radius=8, fill=(34, 197, 94))
    d4.text((105, 582), "✔ Commit suggestion", fill=(255, 255, 255), font=f_pill)

    d4.rounded_rectangle((325, 570, 480, 615), radius=8, fill=(30, 41, 59), outline=(51, 65, 85))
    d4.text((345, 582), "📋 Copy Fix", fill=(226, 232, 240), font=f_pill)

    # Explanation text below
    d4.text((85, 660), "💡 How It Works Under The Hood:", fill=(56, 189, 248), font=f_card_title)
    d4.text((85, 695), "1. Unified diff line offset mapping finds the exact target line in the modified file.\n2. Gemini 2.0 Flash constructs the idiomatic, secure replacement code block.\n3. Formatted using GitHub markdown ```suggestion syntax for 1-click merging.", fill=(203, 213, 225), font=f_sub, spacing=6)

    d4.line((60, H - 90, W - 60, H - 90), fill=(30, 41, 59), width=1)
    d4.text((60, H - 65), "Compatible with GitHub REST API PR Reviews & Webhooks.", fill=(100, 116, 139), font=f_footer)
    d4.text((W - 270, H - 65), "Next: Diff Parser →", fill=(56, 189, 248), font=f_pill)
    s4.save(os.path.join(output_slides_dir, "slide_4.png"))
    slides.append(s4)

    # ==========================================
    # SLIDE 5: UNIFIED DIFF PARSING & GITHUB API
    # ==========================================
    s5 = Image.new("RGB", (W, H), (11, 17, 32))
    d5 = ImageDraw.Draw(s5)
    d5.rounded_rectangle((60, 50, 300, 80), radius=6, fill=(30, 41, 59), outline=(51, 65, 85))
    d5.text((75, 57), "PILLAR 04: GIT PIPELINE", fill=(56, 189, 248), font=f_badge)
    d5.text((W - 160, 57), "Slide 5 of 8", fill=(148, 163, 184), font=f_badge)

    d5.text((60, 100), "Unified Diff Parser & GitHub REST Lifecycle", fill=(248, 250, 252), font=f_title)
    d5.text((60, 142), "How the bot transforms raw Git patches into structured, actionable AST coordinates.", fill=(148, 163, 184), font=f_sub)

    steps_pipe = [
        ("1. Git Patch Extraction", "Accepts standard unified diffs or fetches raw PR diffs directly via GitHub API headers:\nAccept: application/vnd.github.v3.diff", (59, 130, 246)),
        ("2. Hunk & Line Coordinate Tracking", "Parses @@ -line,count +line,count @@ markers to track exact physical line numbers for every addition and modification.", (168, 85, 247)),
        ("3. Hybrid Multi-Pass Evaluation", "Runs deterministic regex security scanner concurrently with Gemini 2.0 Flash context reasoning.", (245, 158, 11)),
        ("4. GitHub Review Submission", "Posts structured inline comments to POST /repos/{owner}/{repo}/pulls/{no}/reviews with verdict status.", (34, 197, 94))
    ]

    for idx, (ptitle, pdesc, paccent) in enumerate(steps_pipe):
        py = 195 + idx * 140
        d5.rounded_rectangle((60, py, W - 60, py + 120), radius=12, fill=(15, 23, 42), outline=(51, 65, 85), width=2)
        d5.rectangle((74, py + 14, 78, py + 42), fill=paccent)
        d5.text((90, py + 16), ptitle, fill=(248, 250, 252), font=f_card_title)
        
        words = pdesc.split("\n")
        d5.text((90, py + 48), words[0], fill=(148, 163, 184), font=f_sub)
        if len(words) > 1:
            d5.text((90, py + 75), words[1], fill=(56, 189, 248), font=f_mono_sm)

    d5.rounded_rectangle((60, 780, W - 60, 860), radius=12, fill=(17, 24, 39), outline=(59, 130, 246))
    d5.text((85, 800), "🌐 UNIVERSAL GIT COMPATIBILITY", fill=(96, 165, 250), font=f_badge)
    d5.text((85, 825), "Operates on raw unified diffs, GitHub PR URLs, GitLab MRs, and local git diff outputs.", fill=(226, 232, 240), font=f_sub)

    d5.line((60, H - 90, W - 60, H - 90), fill=(30, 41, 59), width=1)
    d5.text((60, H - 65), "Fault-tolerant unidiff parsing with automatic raw code fallback.", fill=(100, 116, 139), font=f_footer)
    d5.text((W - 270, H - 65), "Next: Health Score →", fill=(56, 189, 248), font=f_pill)
    s5.save(os.path.join(output_slides_dir, "slide_5.png"))
    slides.append(s5)

    # ==========================================
    # SLIDE 6: HEALTH SCORE & VERDICTS
    # ==========================================
    s6 = Image.new("RGB", (W, H), (11, 17, 32))
    d6 = ImageDraw.Draw(s6)
    d6.rounded_rectangle((60, 50, 310, 80), radius=6, fill=(30, 41, 59), outline=(51, 65, 85))
    d6.text((75, 57), "PILLAR 05: QUALITY GATES", fill=(56, 189, 248), font=f_badge)
    d6.text((W - 160, 57), "Slide 6 of 8", fill=(148, 163, 184), font=f_badge)

    d6.text((60, 100), "0–100 Code Health Score & Merge Verdicts", fill=(248, 250, 252), font=f_title)
    d6.text((60, 142), "Deterministic arithmetic prevents merge subjectivity and enforces objective quality bars.", fill=(148, 163, 184), font=f_sub)

    # Formula Box
    d6.rounded_rectangle((60, 200, W - 60, 340), radius=14, fill=(15, 23, 42), outline=(51, 65, 85), width=2)
    d6.text((85, 220), "SCORING ALGORITHM FORMULA", fill=(56, 189, 248), font=f_badge)
    d6.text((85, 250), "Health Score = Max(0, 100 - (Critical × 25) - (Warning × 10) - (Info × 3))", fill=(248, 250, 252), font=f_card_title)
    d6.text((85, 285), "• CRITICAL (-25 pts): OWASP Top 10, Hardcoded Credentials, RCE, Remote Injections", fill=(248, 113, 113), font=f_sub)
    d6.text((85, 310), "• WARNING (-10 pts): Mutable defaults, swallowed exceptions, unclosed file descriptors", fill=(251, 191, 36), font=f_sub)

    # 3 Verdict Cards
    verdicts = [
        ("✅ APPROVE", "Score: 80 - 100", "Zero critical security vulnerabilities and minimal warnings. PR is safe for production merge.", (34, 197, 94)),
        ("💬 COMMENT", "Score: 60 - 79", "Minor style warnings, performance suggestions, or documentation gaps. Non-blocking review.", (59, 130, 246)),
        ("🛑 REQUEST_CHANGES", "Score: < 60 or Critical ≥ 1", "Active credential leak, SQL injection, or dangerous code execution detected. Merging blocked.", (239, 68, 68))
    ]

    for idx, (vtitle, vscore, vdesc, vcolor) in enumerate(verdicts):
        vy = 360 + idx * 135
        d6.rounded_rectangle((60, vy, W - 60, vy + 115), radius=12, fill=(15, 23, 42), outline=(51, 65, 85), width=2)
        d6.rounded_rectangle((80, vy + 18, 280, vy + 54), radius=6, fill=vcolor)
        d6.text((95, vy + 24), vtitle, fill=(255, 255, 255), font=f_card_title)
        d6.text((300, vy + 25), vscore, fill=(148, 163, 184), font=f_card_title)
        d6.text((85, vy + 68), vdesc, fill=(203, 213, 225), font=f_sub)

    d6.rounded_rectangle((60, 780, W - 60, 860), radius=10, fill=(17, 24, 39), outline=(59, 130, 246))
    d6.text((85, 800), "⚡ CI/CD INTEGRATION READY", fill=(96, 165, 250), font=f_badge)
    d6.text((85, 825), "Seamlessly triggers GitHub Actions status checks to enforce zero-leak merge policies.", fill=(226, 232, 240), font=f_sub)

    d6.line((60, H - 90, W - 60, H - 90), fill=(30, 41, 59), width=1)
    d6.text((60, H - 65), "Tested across thousands of synthetic diff hunks with 100% test pass rate.", fill=(100, 116, 139), font=f_footer)
    d6.text((W - 270, H - 65), "Next: Playground UI →", fill=(56, 189, 248), font=f_pill)
    s6.save(os.path.join(output_slides_dir, "slide_6.png"))
    slides.append(s6)

    # ==========================================
    # SLIDE 7: WEB PLAYGROUND & DASHBOARD
    # ==========================================
    s7 = Image.new("RGB", (W, H), (11, 17, 32))
    d7 = ImageDraw.Draw(s7)
    d7.rounded_rectangle((60, 50, 310, 80), radius=6, fill=(30, 41, 59), outline=(51, 65, 85))
    d7.text((75, 57), "PILLAR 06: DASHBOARD UI", fill=(56, 189, 248), font=f_badge)
    d7.text((W - 160, 57), "Slide 7 of 8", fill=(148, 163, 184), font=f_badge)

    d7.text((60, 100), "Interactive Web Playground (Tailwind Dark Mode)", fill=(248, 250, 252), font=f_title)
    d7.text((60, 142), "Test Git patches and public GitHub PRs instantly with real-time visual auditing feedback.", fill=(148, 163, 184), font=f_sub)

    ui_cards = [
        ("⚡ Dual Input Modes", "Switch seamlessly between pasting raw Git unified diffs / code snippets or pasting any public GitHub PR URL for automated ingestion.", (59, 130, 246)),
        ("🎯 Preset Vulnerability Tests", "Includes 1-click test presets: SQL Injection, Hardcoded AWS Credentials, Insecure Deserialization (Pickle), and Clean Python Code.", (168, 85, 247)),
        ("🔍 Real-Time Filter & Copy", "Filter review findings by Severity (Critical/Warning/Info) or Category (Security/Bug/Style) with one-click fix copy buttons.", (34, 197, 94)),
        ("📄 Markdown & JSON Export", "Download comprehensive audit summaries formatted as GitHub PR comments or machine-readable JSON reports.", (245, 158, 11)),
    ]

    for idx, (utitle, udesc, uaccent) in enumerate(ui_cards):
        uy = 195 + idx * 140
        d7.rounded_rectangle((60, uy, W - 60, uy + 120), radius=12, fill=(15, 23, 42), outline=(51, 65, 85), width=2)
        d7.rectangle((74, uy + 14, 78, uy + 42), fill=uaccent)
        d7.text((90, uy + 16), utitle, fill=(248, 250, 252), font=f_card_title)
        d7.text((90, uy + 50), udesc, fill=(148, 163, 184), font=f_sub)

    d7.rounded_rectangle((60, 780, W - 60, 860), radius=12, fill=(17, 24, 39), outline=(59, 130, 246))
    d7.text((85, 800), "📱 FULLY RESPONSIVE & PRODUCTION SERVED", fill=(96, 165, 250), font=f_badge)
    d7.text((85, 825), "Served directly from FastAPI static assets with zero external frontend build dependencies.", fill=(226, 232, 240), font=f_sub)

    d7.line((60, H - 90, W - 60, H - 90), fill=(30, 41, 59), width=1)
    d7.text((60, H - 65), "Live Dashboard: ai-code-reviewer.onrender.com", fill=(100, 116, 139), font=f_footer)
    d7.text((W - 270, H - 65), "Next: Architecture & Code →", fill=(56, 189, 248), font=f_pill)
    s7.save(os.path.join(output_slides_dir, "slide_7.png"))
    slides.append(s7)

    # ==========================================
    # SLIDE 8: ARCHITECTURE & LIVE LINKS (CTA)
    # ==========================================
    s8 = Image.new("RGB", (W, H), (11, 17, 32))
    d8 = ImageDraw.Draw(s8)
    d8.rounded_rectangle((60, 50, 360, 84), radius=8, fill=(30, 41, 59), outline=(51, 65, 85))
    d8.text((75, 59), "⚡ ARCHITECTURE & PRODUCTION STACK", fill=(56, 189, 248), font=f_badge)
    d8.text((W - 160, 59), "Slide 8 of 8", fill=(148, 163, 184), font=f_badge)

    d8.text((60, 110), "Full-Stack AI Engineering Architecture", fill=(248, 250, 252), font=f_hero)
    d8.text((60, 175), "Production CI/CD microservice delivering automated code review and security auditing.", fill=(148, 163, 184), font=f_sub)

    # Data Flow Box
    d8.rounded_rectangle((60, 230, W - 60, 400), radius=14, fill=(15, 23, 42), outline=(51, 65, 85), width=2)
    d8.text((85, 250), "INFRASTRUCTURE & DATA FLOW PIPELINE", fill=(56, 189, 248), font=f_badge)
    steps = [
        ("Git Diff / PR", "Raw Git Patch\nor GitHub URL"),
        ("Diff Parser", "Unidiff Hunks\n& Line Mapper"),
        ("Dual Scanner", "OWASP Regex\n+ Gemini 2.0"),
        ("Health Engine", "0–100 Score\n& PR Verdict"),
        ("GitHub / Web", "Inline Diff\nFix Suggestions")
    ]
    step_w = 165
    for idx, (stitle, ssub) in enumerate(steps):
        sx = 85 + idx * (step_w + 22)
        d8.rounded_rectangle((sx, 280, sx + step_w, 375), radius=10, fill=(30, 41, 59), outline=(59, 130, 246) if idx==2 else (51, 65, 85))
        d8.text((sx + 10, 295), stitle, fill=(248, 250, 252), font=f_pill)
        d8.text((sx + 10, 325), ssub, fill=(148, 163, 184), font=f_pill_sub, spacing=3)
        if idx < len(steps) - 1:
            d8.text((sx + step_w + 6, 320), "→", fill=(96, 165, 250), font=f_pill)

    # Live Links Box
    d8.rounded_rectangle((60, 430, W - 60, 810), radius=16, fill=(17, 24, 39), outline=(59, 130, 246), width=2)
    d8.text((90, 460), "🚀 EXPLORE THE PROJECT & INSPECT SOURCE CODE", fill=(96, 165, 250), font=f_badge)

    links = [
        ("💻 GitHub Repository", "https://github.com/jayshreeganesh/ai-code-reviewer", "Complete source code, Dockerfile, Pytest suite (10/10 passed) & README."),
        ("🌐 Interactive Web Playground", "https://ai-code-reviewer.onrender.com/", "Test live diffs or paste public GitHub PR URLs for instant AI auditing."),
        ("📖 Swagger OpenAPI Docs", "https://ai-code-reviewer.onrender.com/docs", "Interactive API documentation with request/response schemas for /review/diff & /review/pr.")
    ]

    for idx, (ltitle, lurl, ldesc) in enumerate(links):
        ly = 500 + idx * 95
        d8.rounded_rectangle((85, ly, W - 85, ly + 80), radius=10, fill=(15, 23, 42), outline=(51, 65, 85))
        d8.text((105, ly + 12), ltitle, fill=(248, 250, 252), font=f_pill)
        d8.text((105, ly + 36), lurl, fill=(56, 189, 248), font=f_mono)
        d8.text((105, ly + 58), ldesc, fill=(148, 163, 184), font=f_pill_sub)

    d8.text((60, 840), "Enjoyed this project? Feedback and discussions are always welcome in the comments!", fill=(226, 232, 240), font=f_sub)

    d8.line((60, H - 90, W - 60, H - 90), fill=(30, 41, 59), width=1)
    d8.text((60, H - 65), "AI Engineering Portfolio • Project 4 • FastAPI + Gemini 2.0 Flash + Docker", fill=(100, 116, 139), font=f_footer)
    d8.text((W - 320, H - 65), "Follow & Connect on LinkedIn 🤝", fill=(56, 189, 248), font=f_pill)
    s8.save(os.path.join(output_slides_dir, "slide_8.png"))
    slides.append(s8)

    # Save PDF
    first_slide = slides[0]
    first_slide.save(output_pdf, "PDF", resolution=150.0, save_all=True, append_images=slides[1:])
    print(f"SUCCESS: Generated {len(slides)} slides into {output_pdf}")

if __name__ == "__main__":
    create_carousel()
