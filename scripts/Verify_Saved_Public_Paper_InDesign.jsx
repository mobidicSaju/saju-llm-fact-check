#target "InDesign"
/* Public edition 2026-11-03: portable file discovery, 16 pages / 794 stories.
 * Copyright 2026 박성모. SPDX-License-Identifier: Apache-2.0 */
/* Reopen only the saved paper, independently check native persistence, and
 * leave it visible. Existing unrelated documents are not closed or saved. */
(function () {
    // Optional SAJU_PAPER_OUTPUT selects a directory without embedding a host path.
    // Otherwise locate paper/ in a standalone checkout or the local output tree.
    function locatePaperFolder(filename) {
        var configured = $.getenv("SAJU_PAPER_OUTPUT");
        if (configured) {
            var explicitFolder = Folder(configured);
            if (!File(explicitFolder.fsName + "/" + filename).exists) {
                throw Error("Configured paper directory does not contain " + filename);
            }
            return explicitFolder;
        }
        var cursor = File($.fileName).parent;
        var relativePaths = ["paper", "output/indesign/saju-llm-fact-check"];
        for (var depth = 0; depth < 8; depth++) {
            for (var option = 0; option < relativePaths.length; option++) {
                var candidate = Folder(cursor.fsName + "/" + relativePaths[option]);
                if (File(candidate.fsName + "/" + filename).exists) return candidate;
            }
            if (cursor.parent.fsName === cursor.fsName) break;
            cursor = cursor.parent;
        }
        throw Error("Paper directory not found; set SAJU_PAPER_OUTPUT or place files in paper/.");
    }
    var folder = locatePaperFolder("PAPER_PUBLIC_A4.indd").fsName;
    var source = File(folder + "/PAPER_PUBLIC_A4.indd");
    var report = File(folder + "/indesign-reopen-check.txt");
    var oldInteraction = app.scriptPreferences.userInteractionLevel;
    var process = null, doc = null, notes = [], i;
    var approved = {YoonMyungjoPro730:1, YoonMyungjoPro760:1,
                    YoonGothicPro740:1, YoonGothicPro760:1};
    try {
        if (!source.exists || report.exists) throw Error("Missing source or existing report");
        for (i = app.documents.length - 1; i >= 0; i--) {
            var current = app.documents[i];
            if (current.saved && current.fullName.fsName === source.fsName) {
                if (current.modified) throw Error("Paper has unsaved changes; reopen aborted");
                current.close(SaveOptions.NO);
            }
        }
        app.scriptPreferences.userInteractionLevel = UserInteractionLevels.NEVER_INTERACT;
        doc = app.open(source, true);
        if (doc.pages.length !== 16 || doc.stories.length !== 794 || doc.links.length !== 0) {
            throw Error("Saved document structure differs");
        }
        if (doc.layers[0].name.indexOf("Editable text /") !== 0) throw Error("Wrong layer order");
        for (i = 0; i < doc.stories.length; i++) {
            if (doc.stories[i].overflows) throw Error("Reopened story overflows");
        }
        for (i = 0; i < doc.pages.length; i++) {
            var b = doc.pages[i].bounds;
            if (Math.abs(b[3]-b[1]-595.275591)>.1 || Math.abs(b[2]-b[0]-841.889764)>.1) {
                throw Error("Reopened page is not A4");
            }
        }
        if (doc.fonts.length !== 4) throw Error("Unexpected font count");
        for (i = 0; i < doc.fonts.length; i++) {
            var font = doc.fonts[i];
            if (!approved[font.postscriptName] || font.status !== FontStatus.INSTALLED ||
                !font.allowPDFEmbedding || !font.allowPrinting) throw Error("Unexpected font");
            notes.push("Font: " + font.postscriptName);
        }
        var profile = null;
        for (i = 0; i < app.preflightProfiles.length; i++) {
            if (app.preflightProfiles[i].name === "[Basic]") profile = app.preflightProfiles[i];
        }
        if (profile === null) throw Error("Basic profile unavailable");
        process = app.preflightProcesses.add(doc, profile);
        var waitReturn = process.waitForProcess(60);
        var inventory = String(process.processInventory);
        var result = process.aggregatedResults;
        if (inventory.indexOf("Spread 16") < 0 || !result || result.length < 3 ||
            !(result[2] instanceof Array) || result[2].length !== 0) throw Error("Reopen preflight failed");
        notes.push("Source: " + source.fsName);
        notes.push("InDesign version: " + app.version);
        notes.push("Reopened from disk: true");
        notes.push("Pages: 16; A4: true; Stories: 794; Links: 0; Overset: 0");
        notes.push("Top layer: editable text; filled vectors below");
        notes.push("Preflight wait return: " + waitReturn);
        notes.push("Preflight inventory characters: " + inventory.length);
        notes.push("Native preflight errors: 0");
        notes.push("Saved document modified by verification: " + doc.modified);
        notes.push("Status: passed");
        report.encoding = "UTF-8";
        if (!report.open("w")) throw Error("Cannot write reopen report");
        report.write(notes.join("\n") + "\n");
        report.close();
        app.activeWindow.activePage = doc.pages[0];
        app.activeWindow.zoom(ZoomOptions.FIT_PAGE);
    } finally {
        if (process !== null && process.isValid) process.remove();
        app.scriptPreferences.userInteractionLevel = oldInteraction;
    }
}());
