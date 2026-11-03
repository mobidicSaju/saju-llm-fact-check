#target "InDesign"
/* Public edition 2026-11-03: portable file discovery, 16 pages / 794 stories.
 * Copyright 2026 박성모. SPDX-License-Identifier: Apache-2.0 */
/* Executed locally after explicit user authorization for AppleScript/InDesign.
 * Merely creating this file does not authorize or execute app control.
 * Opens the positioned IDML, checks fonts/overset/A4, runs native preflight,
 * then saves INDD and a separate PDF. Never overwrites the source print PDF.
 * Proprietary source font files are neither copied nor packaged.
 * API references:
 * https://developer.adobe.com/indesign/uxp/dom/api/p/preflight-process/
 * https://developer.adobe.com/indesign/uxp/dom/api/p/preflight-processes/
 * https://developer.adobe.com/indesign/uxp/dom/api/f/font/
 */
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
    var folder = locatePaperFolder("PAPER_PUBLIC_A4.idml");
    var source = File(folder.fsName + "/PAPER_PUBLIC_A4.idml");
    var indd = File(folder.fsName + "/PAPER_PUBLIC_A4.indd");
    var pdf = File(folder.fsName + "/PAPER_PUBLIC_A4_INDESIGN.pdf");
    var report = File(folder.fsName + "/indesign-native-check.txt");
    var preflightReport = File(folder.fsName + "/indesign-preflight.txt");
    var allowed = {
        "YoonMyungjoPro730": true,
        "YoonMyungjoPro760": true,
        "YoonGothicPro740": true,
        "YoonGothicPro760": true
    };
    var doc = null, process = null, oldPDF = null;
    var notes = [], i, font, profile, results;
    var oldInteraction = app.scriptPreferences.userInteractionLevel;

    function writeText(file, text) {
        file.encoding = "UTF-8";
        if (!file.open("w")) throw Error("Cannot write " + file.fsName);
        file.write(text);
        file.close();
    }

    try {
        if (!source.exists) throw Error("Missing IDML: " + source.fsName);
        if (indd.exists || pdf.exists || report.exists || preflightReport.exists) {
            throw Error("Native output/report already exists. Review and move it before a new run; no overwrite performed.");
        }
        app.scriptPreferences.userInteractionLevel = UserInteractionLevels.NEVER_INTERACT;
        doc = app.open(source, true);
        doc.viewPreferences.horizontalMeasurementUnits = MeasurementUnits.POINTS;
        doc.viewPreferences.verticalMeasurementUnits = MeasurementUnits.POINTS;
        if (doc.layers[0].name.indexOf("Editable text /") !== 0) {
            throw Error("Text layer must be above filled diagram vectors.");
        }
        doc.recompose();
        notes.push("Source: " + source.fsName);
        notes.push("InDesign version: " + app.version);
        notes.push("Pages: " + doc.pages.length);
        notes.push("Stories: " + doc.stories.length);
        if (doc.pages.length !== 16) throw Error("Expected 16 pages, got " + doc.pages.length);
        if (doc.stories.length !== 794) throw Error("Expected 794 stories, got " + doc.stories.length);
        notes.push("Format: positioned independent text stories, not a threaded manuscript");

        for (i = 0; i < doc.fonts.length; i++) {
            font = doc.fonts[i];
            if (font.status !== FontStatus.INSTALLED) throw Error("Missing font: " + font.name);
            if (!allowed[font.postscriptName]) throw Error("Non-approved font: " + font.postscriptName);
            if (!font.allowPDFEmbedding || !font.allowPrinting) throw Error("Font does not allow print/PDF use: " + font.postscriptName);
            notes.push("Font: " + font.postscriptName + " / " + font.fontStyleName);
        }
        for (i = 0; i < doc.stories.length; i++) {
            if (doc.stories[i].overflows) throw Error("Overset story at index " + i);
        }
        for (i = 0; i < doc.pages.length; i++) {
            var bounds = doc.pages[i].bounds;
            if (Math.abs((bounds[3] - bounds[1]) - 595.275591) > 0.1 ||
                Math.abs((bounds[2] - bounds[0]) - 841.889764) > 0.1) {
                throw Error("Non-A4 page: " + doc.pages[i].name);
            }
        }
        if (doc.links.length !== 0) throw Error("Unexpected external links: " + doc.links.length);
        notes.push("Overset stories: 0");
        notes.push("Missing/non-approved fonts: 0");
        notes.push("External links: 0");

        // Use an existing Basic profile; do not modify the user's profiles.
        profile = null;
        for (i = 0; i < app.preflightProfiles.length; i++) {
            var candidate = app.preflightProfiles[i];
            if (candidate.name === "[Basic]" || candidate.name === "$ID/[Basic]") {
                profile = candidate;
                break;
            }
        }
        if (profile === null || !profile.isValid) throw Error("The standard Basic preflight profile is unavailable; native preflight remains incomplete.");
        process = app.preflightProcesses.add(doc, profile);
        // InDesign 21.6 returns false here even for a completed process.
        // A separate synthetic overset control confirmed actual error detection.
        var waitResult = process.waitForProcess(60);
        var inventory = String(process.processInventory);
        if (inventory.length === 0 || inventory.indexOf("Spread 16") < 0) {
            throw Error("Native preflight inventory does not cover the complete paper.");
        }
        notes.push("Preflight wait return: " + waitResult + " (21.6 control-tested; not used as success flag)");
        notes.push("Preflight inventory characters: " + inventory.length);
        writeText(preflightReport, String(process.processResults));
        results = process.aggregatedResults;
        if (!results || results.length < 3 || !(results[2] instanceof Array)) {
            throw Error("Unexpected native preflight results format; inspect the report.");
        }
        notes.push("Preflight profile: " + profile.name);
        notes.push("Native preflight errors: " + results[2].length);
        if (results[2].length !== 0) throw Error("Native preflight reports errors; see " + preflightReport.fsName);

        oldPDF = app.pdfExportPreferences.properties;
        app.pdfExportPreferences.pageRange = PageRange.ALL_PAGES;
        app.pdfExportPreferences.exportReaderSpreads = false;
        app.pdfExportPreferences.exportAsSinglePages = false;
        app.pdfExportPreferences.includeSlugWithPDF = false;
        app.pdfExportPreferences.viewPDF = false;
        app.pdfExportPreferences.subsetFontsBelow = 100;
        app.pdfExportPreferences.includeHyperlinks = true;
        app.pdfExportPreferences.includeBookmarks = true;
        app.pdfExportPreferences.exportNonprintingObjects = false;
        app.pdfExportPreferences.exportGuidesAndGrids = false;
        app.pdfExportPreferences.useSecurity = false;
        app.pdfExportPreferences.cropMarks = false;
        app.pdfExportPreferences.bleedMarks = false;
        app.pdfExportPreferences.registrationMarks = false;
        app.pdfExportPreferences.colorBars = false;
        app.pdfExportPreferences.pageInformationMarks = false;
        app.pdfExportPreferences.useDocumentBleedWithPDF = true;
        doc.save(indd);
        doc.exportFile(ExportFormat.PDF_TYPE, pdf, false);
        if (!indd.exists || !pdf.exists || pdf.length <= 0) throw Error("Native export files were not created.");
        notes.push("INDD: " + indd.fsName);
        notes.push("PDF: " + pdf.fsName);
        notes.push("Status: native checks and export completed; rendered PDF visual comparison still required");
        writeText(report, notes.join("\n") + "\n");
    } catch (err) {
        if (!report.exists && doc !== null) {
            notes.push("Status: failed");
            notes.push("Error: " + String(err));
            try { writeText(report, notes.join("\n") + "\n"); } catch (writeError) {}
        }
        throw err;
    } finally {
        if (process !== null && process.isValid) process.remove();
        if (oldPDF !== null) app.pdfExportPreferences.properties = oldPDF;
        app.scriptPreferences.userInteractionLevel = oldInteraction;
        // Keep only the newly opened document visible for human visual review.
        // Existing documents are never closed or saved by this script.
    }
}());
