# RAPP Step Guide

Guide the user through a specific RAPP pipeline step. The argument should be the step number (1-14).

All operations use the single **RAPP** agent with different actions.

## Step Details

Based on the step number provided ($ARGUMENTS), give detailed guidance:

### Step 1: Discovery Call
**What to do**: Prepare for and process a discovery call
**RAPP Actions**:
- `prepare_discovery_call` - Generate call prep guide
- `process_transcript` - Process transcript after call
**Inputs needed**: customer_name, industry (for prep); customer_name, transcript (for processing)
**Outputs**: Discovery guide, extracted problem statements, data sources, stakeholders, success criteria

### Step 2: QG1 - Transcript Validation
**What to do**: Validate discovery data completeness
**RAPP Action**: `execute_quality_gate` with `gate="QG1"`
**Inputs needed**: customer_name, project_name, input_data (discovery data)
**Outputs**: PASS/CLARIFY/FAIL decision with scores

### Step 3: MVP Poke Document
**What to do**: Generate customer proposal document
**RAPP Actions**:
- `generate_mvp_poke` - Quick MVP proposal
- `generate_full_mvp_document` - Complete customer-ready document
- `prioritize_features` - Feature prioritization
- `define_scope` - Scope boundaries
**Inputs needed**: customer_name, project_name, problem_statement, discovery_data
**Outputs**: Full MVP document with features, timeline, risks

### Step 4: QG2 - Customer Validation
**What to do**: Get customer sign-off, LOCK SCOPE
**RAPP Action**: `execute_quality_gate` with `gate="QG2"`
**Inputs needed**: input_data (MVP document + customer response)
**Outputs**: PROCEED/REVISE/HOLD decision, scope lock confirmation

### Step 5: Generate Agent Code
**What to do**: Create Python agent following BasicAgent pattern
**RAPP Actions**:
- `generate_agent_code` - Full agent code
- `generate_agent_metadata` - Metadata schema only
**Inputs needed**: agent_name, agent_description, features, data_sources
**Outputs**: Complete Python agent code

### Step 6: QG3 - Code Quality Review
**What to do**: Validate code quality and security
**RAPP Actions**:
- `execute_quality_gate` with `gate="QG3"`
- `review_code` - Detailed code review
**Inputs needed**: input_data (code + spec) or existing_code
**Outputs**: PASS/FIX_REQUIRED/FAIL with specific fixes

### Step 7: Deploy Prototype
**What to do**: Deploy agent to Azure
**RAPP Action**: `generate_deployment_config`
**Inputs needed**: agent_name, customer_name
**Outputs**: Deployment configuration and steps

### Step 8: QG4 - Demo Review
**What to do**: Review prototype demo using Waiter Pattern
**RAPP Action**: `execute_quality_gate` with `gate="QG4"`
**Inputs needed**: input_data (demo/prototype data)
**Outputs**: PASS/POLISH/FAIL decision

### Step 9: Create Video Demo
**What to do**: Generate demo script for video
**Manual step** - Use MVP document and demo data to create script

### Step 10: QG5 - Final Demo Review
**What to do**: Executive readiness review
**RAPP Action**: `execute_quality_gate` with `gate="QG5"`
**Inputs needed**: input_data (demo script + video data)
**Outputs**: APPROVE/MINOR_REVISIONS/MAJOR_REVISIONS/REJECT

### Step 11: Iteration Loop
**What to do**: Process feedback and iterate
**RAPP Action**: `get_step_checklist` with `step=11`
**Manual classification** of feedback into bug/polish/feature/scope creep

### Step 12: Production Deployment
**What to do**: Deploy to production
**Manual step** with `generate_deployment_config` for reference

### Step 13: QG6 - Post-Deployment Audit
**What to do**: Audit deployed system health
**RAPP Action**: `execute_quality_gate` with `gate="QG6"`
**Inputs needed**: input_data (deployment metrics)
**Outputs**: GREEN/YELLOW/RED status with recommendations

### Step 14: Scale & Maintain
**What to do**: Plan for scaling and maintenance
**RAPP Action**: `get_step_checklist` with `step=14`
**Review audit results and plan optimizations**

## After providing guidance:

Ask the user if they want to:
1. Execute this step now (using the appropriate RAPP action)
2. See the checklist for this step (`get_step_checklist`)
3. Move to a different step
4. Update their project progress (use ProjectTracker agent)

Remember to always update ProjectTracker after completing a step!
