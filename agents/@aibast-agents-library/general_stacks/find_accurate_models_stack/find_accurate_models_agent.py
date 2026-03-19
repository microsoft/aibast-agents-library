"""
Find Accurate Models Agent

Searches and compares AI/ML models by accuracy benchmarks, deployment
readiness, and cost metrics to help teams select the best model for their needs.

Where a real deployment would query model registries and MLOps platforms,
this agent uses a synthetic data layer so it runs anywhere without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/find-accurate-models",
    "version": "1.0.0",
    "display_name": "Find Accurate Models",
    "description": "AI/ML model search and comparison by accuracy benchmarks, deployment readiness, and cost analysis.",
    "author": "AIBAST",
    "tags": ["ai", "ml", "model-selection", "benchmarks", "accuracy", "deployment"],
    "category": "general",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_MODEL_CATALOG = {
    "MDL-001": {
        "id": "MDL-001", "name": "SentimentBERT-v3", "task": "Sentiment Analysis",
        "framework": "PyTorch", "parameters": "110M", "size_mb": 438,
        "accuracy": 0.943, "f1_score": 0.938, "latency_ms": 45,
        "training_data": "200K labeled reviews", "last_updated": "2025-09-15",
        "license": "Apache 2.0", "provider": "Internal ML Team",
    },
    "MDL-002": {
        "id": "MDL-002", "name": "DocClassifier-XL", "task": "Document Classification",
        "framework": "TensorFlow", "parameters": "340M", "size_mb": 1350,
        "accuracy": 0.967, "f1_score": 0.961, "latency_ms": 120,
        "training_data": "500K documents, 45 categories", "last_updated": "2025-10-01",
        "license": "MIT", "provider": "AI Research Lab",
    },
    "MDL-003": {
        "id": "MDL-003", "name": "ChurnPredictor-v2", "task": "Churn Prediction",
        "framework": "scikit-learn", "parameters": "2.5M", "size_mb": 12,
        "accuracy": 0.891, "f1_score": 0.874, "latency_ms": 8,
        "training_data": "150K customer records, 24-month history", "last_updated": "2025-08-20",
        "license": "Proprietary", "provider": "Data Science Team",
    },
    "MDL-004": {
        "id": "MDL-004", "name": "NER-Finance-v4", "task": "Named Entity Recognition",
        "framework": "spaCy", "parameters": "85M", "size_mb": 320,
        "accuracy": 0.952, "f1_score": 0.947, "latency_ms": 32,
        "training_data": "80K financial documents", "last_updated": "2025-10-15",
        "license": "Apache 2.0", "provider": "NLP Team",
    },
    "MDL-005": {
        "id": "MDL-005", "name": "ImageQuality-ResNet", "task": "Image Quality Assessment",
        "framework": "PyTorch", "parameters": "25M", "size_mb": 98,
        "accuracy": 0.928, "f1_score": 0.921, "latency_ms": 15,
        "training_data": "100K images with quality labels", "last_updated": "2025-07-10",
        "license": "MIT", "provider": "Computer Vision Team",
    },
    "MDL-006": {
        "id": "MDL-006", "name": "FraudDetector-Ensemble", "task": "Fraud Detection",
        "framework": "XGBoost + PyTorch", "parameters": "50M", "size_mb": 215,
        "accuracy": 0.978, "f1_score": 0.965, "latency_ms": 25,
        "training_data": "2M transactions, 18 months", "last_updated": "2025-11-01",
        "license": "Proprietary", "provider": "Security ML Team",
    },
}

_DEPLOYMENT_REQUIREMENTS = {
    "cpu_inference": {"min_ram_gb": 4, "min_cores": 2, "max_latency_ms": 200, "cost_per_1k_inferences": 0.02},
    "gpu_inference": {"min_ram_gb": 8, "gpu_vram_gb": 8, "max_latency_ms": 50, "cost_per_1k_inferences": 0.15},
    "edge_deployment": {"min_ram_gb": 2, "max_model_size_mb": 200, "max_latency_ms": 30, "cost_per_1k_inferences": 0.005},
    "serverless": {"max_cold_start_ms": 3000, "max_model_size_mb": 500, "cost_per_1k_inferences": 0.05},
}

_PRICING_TIERS = {
    "development": {"monthly_cost": 0, "inference_limit": 10000, "support": "Community", "sla": "None"},
    "standard": {"monthly_cost": 499, "inference_limit": 500000, "support": "Email (48h)", "sla": "99.5%"},
    "professional": {"monthly_cost": 1999, "inference_limit": 5000000, "support": "Priority (4h)", "sla": "99.9%"},
    "enterprise": {"monthly_cost": 7999, "inference_limit": -1, "support": "Dedicated (1h)", "sla": "99.99%"},
}


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _search_models(task_filter=None, min_accuracy=0.0):
    results = []
    for mid, model in _MODEL_CATALOG.items():
        if task_filter and task_filter.lower() not in model["task"].lower():
            continue
        if model["accuracy"] >= min_accuracy:
            results.append(model)
    return sorted(results, key=lambda m: m["accuracy"], reverse=True)


def _check_deployment_readiness(model_id, target="cpu_inference"):
    model = _MODEL_CATALOG.get(model_id)
    if not model:
        return None
    reqs = _DEPLOYMENT_REQUIREMENTS.get(target, {})
    checks = []
    if "max_model_size_mb" in reqs:
        ok = model["size_mb"] <= reqs["max_model_size_mb"]
        checks.append({"check": "Model Size", "status": "Pass" if ok else "Fail", "detail": f"{model['size_mb']}MB vs {reqs['max_model_size_mb']}MB max"})
    if "max_latency_ms" in reqs:
        ok = model["latency_ms"] <= reqs["max_latency_ms"]
        checks.append({"check": "Latency", "status": "Pass" if ok else "Fail", "detail": f"{model['latency_ms']}ms vs {reqs['max_latency_ms']}ms max"})
    passed = sum(1 for c in checks if c["status"] == "Pass")
    return {"model": model["name"], "target": target, "checks": checks, "passed": passed, "total": len(checks), "ready": passed == len(checks)}


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class FindAccurateModelsAgent(BasicAgent):
    """
    AI/ML model search and comparison agent.

    Operations:
        model_search         - search models by task and accuracy threshold
        accuracy_benchmark   - detailed accuracy comparison across models
        deployment_readiness - check if a model meets deployment requirements
        cost_comparison      - compare hosting and inference costs
    """

    def __init__(self):
        self.name = "FindAccurateModelsAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "model_search", "accuracy_benchmark",
                            "deployment_readiness", "cost_comparison",
                        ],
                        "description": "The model search operation to perform",
                    },
                    "task_filter": {
                        "type": "string",
                        "description": "Filter models by task type",
                    },
                    "model_id": {
                        "type": "string",
                        "description": "Model ID for detailed inspection (e.g. 'MDL-001')",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "model_search")
        dispatch = {
            "model_search": self._model_search,
            "accuracy_benchmark": self._accuracy_benchmark,
            "deployment_readiness": self._deployment_readiness,
            "cost_comparison": self._cost_comparison,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}"
        return handler(kwargs)

    # ── model_search ───────────────────────────────────────────
    def _model_search(self, params):
        task = params.get("task_filter", "")
        models = _search_models(task_filter=task if task else None)
        rows = ""
        for m in models:
            rows += f"| {m['id']} | {m['name']} | {m['task']} | {m['accuracy']:.1%} | {m['latency_ms']}ms | {m['framework']} |\n"
        filter_note = f" (filtered by: '{task}')" if task else ""
        return (
            f"**AI/ML Model Search Results{filter_note}**\n\n"
            f"| ID | Name | Task | Accuracy | Latency | Framework |\n|---|---|---|---|---|---|\n"
            f"{rows}\n"
            f"**Total Models:** {len(models)}\n"
            f"**Highest Accuracy:** {models[0]['name']} ({models[0]['accuracy']:.1%})\n"
            f"**Lowest Latency:** {min(models, key=lambda m: m['latency_ms'])['name']} ({min(m['latency_ms'] for m in models)}ms)\n\n"
            f"Source: [Model Registry + MLOps Platform]\nAgents: FindAccurateModelsAgent"
        )

    # ── accuracy_benchmark ─────────────────────────────────────
    def _accuracy_benchmark(self, params):
        models = sorted(_MODEL_CATALOG.values(), key=lambda m: m["accuracy"], reverse=True)
        rows = ""
        for m in models:
            rows += f"| {m['name']} | {m['task']} | {m['accuracy']:.1%} | {m['f1_score']:.1%} | {m['parameters']} | {m['training_data'][:30]} |\n"
        top = models[0]
        return (
            f"**Accuracy Benchmark Comparison**\n\n"
            f"| Model | Task | Accuracy | F1 Score | Parameters | Training Data |\n|---|---|---|---|---|---|\n"
            f"{rows}\n"
            f"**Top Performer:** {top['name']} ({top['accuracy']:.1%} accuracy, {top['f1_score']:.1%} F1)\n\n"
            f"**Accuracy Distribution:**\n"
            f"- 95%+: {sum(1 for m in models if m['accuracy'] >= 0.95)} models\n"
            f"- 90-95%: {sum(1 for m in models if 0.90 <= m['accuracy'] < 0.95)} models\n"
            f"- Below 90%: {sum(1 for m in models if m['accuracy'] < 0.90)} models\n\n"
            f"Source: [Benchmark Suite + Model Registry]\nAgents: FindAccurateModelsAgent"
        )

    # ── deployment_readiness ───────────────────────────────────
    def _deployment_readiness(self, params):
        model_id = params.get("model_id", "MDL-001")
        model = _MODEL_CATALOG.get(model_id)
        if not model:
            return f"Model '{model_id}' not found. Available: {', '.join(_MODEL_CATALOG.keys())}"
        target_rows = ""
        for target in _DEPLOYMENT_REQUIREMENTS:
            result = _check_deployment_readiness(model_id, target)
            status = "Ready" if result["ready"] else "Not Ready"
            target_rows += f"| {target} | {result['passed']}/{result['total']} checks | {status} |\n"
        detail_rows = ""
        for target, reqs in _DEPLOYMENT_REQUIREMENTS.items():
            result = _check_deployment_readiness(model_id, target)
            for check in result["checks"]:
                detail_rows += f"| {target} | {check['check']} | {check['status']} | {check['detail']} |\n"
        return (
            f"**Deployment Readiness: {model['name']}**\n\n"
            f"| Property | Value |\n|---|---|\n"
            f"| Model Size | {model['size_mb']} MB |\n"
            f"| Latency | {model['latency_ms']} ms |\n"
            f"| Framework | {model['framework']} |\n"
            f"| Parameters | {model['parameters']} |\n\n"
            f"**Target Compatibility:**\n\n"
            f"| Target | Checks Passed | Status |\n|---|---|---|\n"
            f"{target_rows}\n"
            f"**Detailed Checks:**\n\n"
            f"| Target | Check | Result | Detail |\n|---|---|---|---|\n"
            f"{detail_rows}\n\n"
            f"Source: [MLOps Platform + Infrastructure]\nAgents: FindAccurateModelsAgent"
        )

    # ── cost_comparison ────────────────────────────────────────
    def _cost_comparison(self, params):
        tier_rows = ""
        for tier, info in _PRICING_TIERS.items():
            limit = f"{info['inference_limit']:,}" if info['inference_limit'] > 0 else "Unlimited"
            tier_rows += f"| {tier.title()} | ${info['monthly_cost']:,}/mo | {limit} | {info['support']} | {info['sla']} |\n"
        infra_rows = ""
        for target, reqs in _DEPLOYMENT_REQUIREMENTS.items():
            infra_rows += f"| {target} | ${reqs['cost_per_1k_inferences']:.3f} | {reqs.get('min_ram_gb', 'N/A')} GB | {reqs.get('max_latency_ms', 'N/A')} ms |\n"
        monthly_100k = {t: reqs["cost_per_1k_inferences"] * 100 for t, reqs in _DEPLOYMENT_REQUIREMENTS.items()}
        cost_lines = "\n".join(f"- {t}: ${c:.2f}/month" for t, c in monthly_100k.items())
        return (
            f"**Cost Comparison**\n\n"
            f"**Pricing Tiers:**\n\n"
            f"| Tier | Monthly Cost | Inference Limit | Support | SLA |\n|---|---|---|---|---|\n"
            f"{tier_rows}\n"
            f"**Infrastructure Cost per 1K Inferences:**\n\n"
            f"| Target | Cost/1K | Min RAM | Max Latency |\n|---|---|---|---|\n"
            f"{infra_rows}\n"
            f"**Estimated Monthly Cost (100K inferences):**\n{cost_lines}\n\n"
            f"Source: [Pricing Engine + Cloud Cost Calculator]\nAgents: FindAccurateModelsAgent"
        )


if __name__ == "__main__":
    agent = FindAccurateModelsAgent()
    for op in ["model_search", "accuracy_benchmark", "deployment_readiness", "cost_comparison"]:
        print("=" * 60)
        print(agent.perform(operation=op, model_id="MDL-001"))
        print()
