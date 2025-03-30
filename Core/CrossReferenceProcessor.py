#!/usr/bin/env python3
# File: CrossReferenceProcessor.py
# Path: AIDEV-GitHub/Core/CrossReferenceProcessor.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-29
# Last Modified: 2025-03-29  10:00PM
# Description: Module for processing cross-references between Project Himalaya documents

import re
from typing import Dict, Any, List, Optional, Match, Pattern

from Utils.LoggingManager import GetLogger

def ProcessCrossReferences(Content: str, DocumentRegistry: Dict[str, Dict[str, Any]]) -> str:
    """
    Process cross-references in document content.
    
    Handles the following reference types:
    1. Document references [XX-XX]
    2. Section references [XX-XX §X.X]
    3. Decision references [DECISION-YYYYMMDD-N]
    
    Args:
        Content: Document content as string
        DocumentRegistry: Registry of documents for cross-reference resolution
    
    Returns:
        str: Document content with processed cross-references
    """
    Logger = GetLogger("CrossReferenceProcessor")
    
    # Process document references [XX-XX]
    def ReplaceDocRef(Match: Match) -> str:
        DocID = Match.group(1)
        if DocID in DocumentRegistry:
            DocInfo = DocumentRegistry[DocID]
            Title = DocInfo.get("title", DocID)
            URL = DocInfo.get("url", "")
            return f"[{DocID}]({URL})"
        return Match.group(0)  # Keep original if not found
    
    Pattern = r'\[(\d{2}-\d{2})\]'
    Content = re.sub(Pattern, ReplaceDocRef, Content)
    
    # Process section references [XX-XX §X.X]
    def ReplaceSectionRef(Match: Match) -> str:
        DocID = Match.group(1)
        Section = Match.group(2)
        
        if DocID in DocumentRegistry:
            DocInfo = DocumentRegistry[DocID]
            URL = DocInfo.get("url", "")
            
            # Create anchor from section reference
            Anchor = Section.lower().replace('.', '')
            
            return f"[{DocID} §{Section}]({URL}#{Anchor})"
        return Match.group(0)  # Keep original if not found
    
    Pattern = r'\[(\d{2}-\d{2}) §(\d+\.\d+)\]'
    Content = re.sub(Pattern, ReplaceSectionRef, Content)
    
    # Process decision references [DECISION-YYYYMMDD-N]
    def ReplaceDecisionRef(Match: Match) -> str:
        DecisionID = Match.group(1)
        
        # Look for decision document in registry
        for DocID, DocInfo in DocumentRegistry.items():
            Title = DocInfo.get("title", "")
            if Title.startswith("DECISION") and DecisionID in Title:
                URL = DocInfo.get("url", "")
                Anchor = DecisionID.lower()
                return f"[{DecisionID}]({URL}#{Anchor})"
        
        # If not found, link to governance category
        return f"[{DecisionID}]({{{{ site.baseurl }}}}/docs/governance/decisions/#{DecisionID.lower()})"
    
    Pattern = r'\[(DECISION-\d{8}-\d+)\]'
    Content = re.sub(Pattern, ReplaceDecisionRef, Content)
    
    return Content

def ExtractReferences(Content: str) -> Dict[str, List[str]]:
    """
    Extract all references from document content.
    
    Args:
        Content: Document content as string
    
    Returns:
        Dict[str, List[str]]: Dictionary of reference types and their values
            Keys: 'documents', 'sections', 'decisions'
    """
    References = {
        "documents": [],
        "sections": [],
        "decisions": []
    }
    
    # Extract document references [XX-XX]
    DocPattern = r'\[(\d{2}-\d{2})\]'
    DocMatches = re.finditer(DocPattern, Content)
    for Match in DocMatches:
        DocID = Match.group(1)
        if DocID not in References["documents"]:
            References["documents"].append(DocID)
    
    # Extract section references [XX-XX §X.X]
    SectionPattern = r'\[(\d{2}-\d{2}) §(\d+\.\d+)\]'
    SectionMatches = re.finditer(SectionPattern, Content)
    for Match in SectionMatches:
        DocID = Match.group(1)
        Section = Match.group(2)
        SectionRef = f"{DocID} §{Section}"
        if SectionRef not in References["sections"]:
            References["sections"].append(SectionRef)
        
        # Also add document ID to document references
        if DocID not in References["documents"]:
            References["documents"].append(DocID)
    
    # Extract decision references [DECISION-YYYYMMDD-N]
    DecisionPattern = r'\[(DECISION-\d{8}-\d+)\]'
    DecisionMatches = re.finditer(DecisionPattern, Content)
    for Match in DecisionMatches:
        DecisionID = Match.group(1)
        if DecisionID not in References["decisions"]:
            References["decisions"].append(DecisionID)
    
    return References

def ValidateReferences(References: Dict[str, List[str]], DocumentRegistry: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Validate references against the document registry.
    
    Args:
        References: Dictionary of references from ExtractReferences
        DocumentRegistry: Registry of documents for cross-reference validation
    
    Returns:
        Dict[str, List[str]]: Dictionary of invalid references by type
    """
    InvalidRefs = {
        "documents": [],
        "sections": [],
        "decisions": []
    }
    
    # Validate document references
    for DocID in References["documents"]:
        if DocID not in DocumentRegistry:
            InvalidRefs["documents"].append(DocID)
    
    # Validate section references
    for SectionRef in References["sections"]:
        DocID = SectionRef.split(" §")[0]
        if DocID not in DocumentRegistry:
            InvalidRefs["sections"].append(SectionRef)
    
    # Validate decision references
    # For decisions, we need to search by title since they're not keyed by ID
    for DecisionID in References["decisions"]:
        Found = False
        for DocInfo in DocumentRegistry.values():
            Title = DocInfo.get("title", "")
            if Title.startswith("DECISION") and DecisionID in Title:
                Found = True
                break
        
        if not Found:
            InvalidRefs["decisions"].append(DecisionID)
    
    return InvalidRefs

def CreateReferenceMap(DocumentRegistry: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Create a map of documents that reference each document.
    
    Args:
        DocumentRegistry: Registry of documents with extracted references
    
    Returns:
        Dict[str, List[str]]: Dictionary mapping document IDs to lists of document IDs that reference them
    """
    ReferenceMap = {}
    
    # Initialize empty list for each document
    for DocID in DocumentRegistry:
        ReferenceMap[DocID] = []
    
    # Build reference map
    for DocID, DocInfo in DocumentRegistry.items():
        if "references" in DocInfo:
            for RefID in DocInfo["references"]:
                if RefID in ReferenceMap:
                    ReferenceMap[RefID].append(DocID)
    
    return ReferenceMap

def UpdateReferenceLinks(Content: str, CurrentDocID: str, ReferenceMap: Dict[str, List[str]]) -> str:
    """
    Add reference links section to document content.
    
    Args:
        Content: Document content as string
        CurrentDocID: ID of the current document
        ReferenceMap: Map of document references from CreateReferenceMap
    
    Returns:
        str: Document content with added reference links section
    """
    # Check if this document is referenced by others
    if CurrentDocID not in ReferenceMap or not ReferenceMap[CurrentDocID]:
        return Content  # No references to this document
    
    # Build reference links section
    ReferencingDocs = ReferenceMap[CurrentDocID]
    
    ReferenceSection = "\n\n## Referenced By\n\n"
    ReferenceSection += "This document is referenced by the following documents:\n\n"
    
    for DocID in sorted(ReferencingDocs):
        ReferenceSection += f"- [{DocID}]({{{{ site.baseurl }}}}/docs/{DocID}/)\n"
    
    # Add to content
    return Content + ReferenceSection

def ProcessCodeLinks(Content: str) -> str:
    """
    Process code links in document content.
    
    Handles links to code files or specific functions.
    
    Args:
        Content: Document content as string
    
    Returns:
        str: Document content with processed code links
    """
    # Process file references `FileName.py`
    def ReplaceFileRef(Match: Match) -> str:
        FileName = Match.group(1)
        ExtMatch = Match.group(2)
        BaseURL = "https://github.com/CallMeChewy/ProjectHimalaya/blob/main"
        
        # Different handling based on file extension
        if ExtMatch == '.py':
            return f"[`{FileName}{ExtMatch}`]({BaseURL}/{FileName}{ExtMatch})"
        elif ExtMatch == '.md':
            # For MD files, link to documentation site instead
            DocID = FileName.split('-')[-1] if '-' in FileName else FileName
            return f"[`{FileName}{ExtMatch}`]({{{{ site.baseurl }}}}/docs/{DocID}/)"
        else:
            return f"`{FileName}{ExtMatch}`"
    
    Pattern = r'`([A-Za-z0-9_-]+)(\.[a-z]+)`'
    Content = re.sub(Pattern, ReplaceFileRef, Content)
    
    # Process function references `FunctionName()`
    def ReplaceFunctionRef(Match: Match) -> str:
        FunctionName = Match.group(1)
        return f"`{FunctionName}()`"
    
    Pattern = r'`([A-Z][a-zA-Z0-9]+)\(\)`'
    Content = re.sub(Pattern, ReplaceFunctionRef, Content)
    
    return Content