-- =====================================================================
-- Hendrix QMS  -  Step 49: Spanish versions of SOPs and online courses
--
--   The app can show every screen in Spanish (EN / ES switch, no SQL needed).
--   SOP and course TEXT is data, so its Spanish version is kept with the record:
--     hx_sops.es                 Spanish title, purpose, scope, steps ... of the current text
--     hx_training_courses.es     Spanish lessons and quiz of the current content
--   A manager makes it with "Translate to Spanish (AI)" (SOPs: Edit access for a draft,
--   Full access once published; courses: Full access to Training). Each Spanish version
--   remembers which English text it was made from: when the English changes, Spanish
--   readers see the English again with a note until it is translated again.
--   The English SOP stays the approved record (PDF, signatures, versions).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-48.
-- Safe to run more than once.
-- =====================================================================

alter table hx_sops add column if not exists es jsonb;
alter table hx_training_courses add column if not exists es jsonb;

notify pgrst, 'reload schema';
select 'Hendrix step 49 (Spanish SOPs and courses) installed' as result;
