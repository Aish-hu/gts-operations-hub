# Kubernetes — browser-only lab checklist

Use https://killercoda.com/ and choose an interactive Kubernetes scenario with a pre-provisioned cluster. Scenarios and their availability may change.

No local Docker, Podman, Kubernetes or Minikube installation is needed.

## Lab 1: Pods and Deployments

In the hosted Kubernetes terminal:

```bash
kubectl create deployment hello --image=nginx:alpine
kubectl get deployments
kubectl get pods -o wide
kubectl scale deployment hello --replicas=2
kubectl get pods
```

## Lab 2: Service discovery

```bash
kubectl expose deployment hello --port=80 --target-port=80 --type=ClusterIP
kubectl get services
kubectl describe service hello
```

## Lab 3: Self-healing

```bash
kubectl get pods -l app=hello
kubectl delete pod -l app=hello
kubectl get pods -w
```

Stop watching with Ctrl+C. Kubernetes Deployment should replace deleted pods.

## Lab 4: Inspect and clean up

```bash
kubectl describe deployment hello
kubectl get events --sort-by=.lastTimestamp
kubectl delete service hello
kubectl delete deployment hello
```

Capture screenshots showing deployments, services, replica scaling, and pod replacement. This is a **separate Kubernetes training lab**, not a deployment of GTS Operations Hub itself.
