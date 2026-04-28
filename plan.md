## Plan: CS Master's Program Recommender

Convert the current music recommender into a CS master's program recommender that uses locally stored program pages or text files for simple retrieval and explanation, without vector embeddings or a paid API. The system remains lightweight: a student profile is matched against program facts, top programs are ranked, and explanations are grounded in retrieved local text.

**Steps**

1. Reframe the domain and schema  
   - Replace song and music concepts with CS master's program concepts.  
   - Redefine the data model around university, location, delivery mode, tuition, application fee, GRE requirement, duration, ranking tier, visa support, graduation rate, and specialization areas.  
   - Redefine the user profile around budget, willingness to take GRE, sensitivity to application fees, location preference, online vs in-person preference, visa needs, ranking preference, research vs industry preference, and target time to graduation.

2. Create the local data corpus and retrieval inputs  
   - Have the agent create the local files automatically.  
   - Replace the song dataset with a curated CS program dataset, or add a program CSV plus per-program text files.  
   - Keep all source material local and based on public program information so retrieval works offline.  
   - Use simple text chunks or per-program notes as retrieval targets. No vector database is required.

3. Refactor the recommender core  
   - Rewrite scoring logic to rank programs instead of songs.  
   - Keep the load, score, and recommend function structure, but adapt features to program fit.  
   - Add explanations that cite retrieved facts and highlight tradeoffs such as cost, visa support, ranking, GRE requirement, application fees, and schedule flexibility.  
   - Preserve existing class structure where useful, but update dataclasses and behavior to the new domain.

4. Add a simple local retrieval layer  
   - Implement keyword and field matching over local program notes.  
   - Retrieve relevant program content before explanation generation.  
   - Keep retrieval deterministic and beginner-friendly.  
   - Do not use embeddings or vector search in this version.

5. Update CLI and sample personas  
   - Replace music profiles with applicant personas such as budget-focused, international applicant, online-first, research-oriented, and ranking-focused profiles.  
   - Update output labels and formatting to programs and admissions factors.  
   - Ensure CLI demonstrates ranking plus retrieval-backed explanations.

6. Rewrite tests and validation  
   - Replace song fixtures with representative CS programs.  
   - Test ranking behavior for contrasting profiles.  
   - Test that explanations are non-empty and grounded in retrieved facts.  
   - Add retrieval tests to validate expected text matches.  
   - Add specific checks for GRE-required vs GRE-optional programs and varying application fees.

7. Design and architecture  
   - Include a short system diagram with retriever, agent, evaluator or tester, human review, and local data store.  
   - Show clear data flow from input to processing to output.  
   - Include explicit human or test checkpoints.  
   - Use this workflow: student profile or question → retrieve relevant program text → score and rank candidates → generate explanation → run tests and human review → final output.

8. Documentation and portfolio framing  
   - Rewrite README so it explicitly names the original Modules 1 to 3 project and summarizes original goals and capabilities in 2 to 3 sentences.  
   - Add title and summary of the new project, architecture overview, setup instructions, 2 to 3 sample interactions, design decisions, testing summary, and reflection.  
   - Embed the system diagram PNG from assets in README.  
   - Rewrite model card to cover intended use, data sources, limitations, bias and fairness concerns, and scope boundaries.

9. Reliability and evaluation  
   - Include at least one reliability method such as unit tests, confidence scoring, logging and error handling, or human evaluation.  
   - Summarize results clearly, for example tests passed, failure modes, and improvement after validation changes.  
   - Ensure evidence of performance is included, not only claims.

**Verification**

1. Run CLI with multiple applicant personas and confirm top programs change appropriately with profile constraints.  
2. Run tests and confirm ranking, retrieval, and explanation checks pass.  
3. Manually inspect explanations to confirm they reference retrieved local facts instead of unsupported claims.  
4. Confirm project runs fully offline with local files only.

**Decisions**

- Use local file retrieval instead of embeddings or vector search.  
- Keep implementation deterministic and beginner-appropriate.  
- Include GRE requirement and application fee as core recommendation factors.  
- Use automated tests plus human spot checks for reliability.  
- Keep existing project structure and refactor in place rather than rebuilding from scratch.

**Further Considerations**

1. Choose corpus format: single CSV plus summaries or separate text files per program. Recommendation is separate text files for easier retrieval and explanation quality.  
2. Choose explanation strategy: purely rule-based text or retrieval-backed explanation. Recommendation is rule-based ranking plus retrieval-backed explanations for best clarity at this scope.