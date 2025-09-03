# MongoDB Templates for Kubernetes/OpenShift

שני templates מתקדמים לפריסת MongoDB במיכלים, מבוססים על הדפוסים מהמבחן המתקדם.

## 📁 קבצי Template

### `deployment-complete.yaml` - גישה רגילה
- **מתאים לפיתוח** ופרודקשן פשוט
- **Deployment** עם PVC נפרד
- **פריסה מהירה** ופשוטה
- **רכיב יחיד** - לא מתאים לhigh availability

### `statefulset-complete.yaml` - גישה מתקדמת
- **מתאים לפרודקשן** וhigh availability
- **StatefulSet** עם replica sets
- **אחסון אוטומטי** לכל pod
- **רשת יציבה** עם headless service

---

## 🚀 איך להשתמש

### משתני Environment הנדרשים

```bash
# בסיסיים
export APP_NAME="my-app"
export DATABASE_NAME="mydatabase"  
export COLLECTION_NAME="mycollection"
export MONGO_VERSION="8.0"
export STORAGE_SIZE="5Gi"
export STORAGE_CLASS="gp2"

# אבטחה
export MONGO_ROOT_PASSWORD="your-secure-password"
export MONGO_REPLICA_SET_KEY="your-replica-set-key"  # רק לStatefulSet

# משאבים
export MONGO_CPU_REQUEST="200m"
export MONGO_MEMORY_REQUEST="256Mi"
export MONGO_CPU_LIMIT="500m"
export MONGO_MEMORY_LIMIT="512Mi"

# StatefulSet ספציפי
export MONGO_REPLICAS="3"  # מספר replicas
export NAMESPACE="default"
export CONFIG_CHECKSUM="$(date +%s)"  # לכפות restart
```

---

## 📋 השוואה מפורטת

| תכונה | Deployment | StatefulSet |
|--------|------------|-------------|
| **מהירות פריסה** | מהירה | איטית יותר |
| **פשטות** | פשוט מאוד | מורכב יותר |
| **זהות Pod** | שם אקראי | שם קבוע |
| **סדר פריסה** | כל הpods יחד | בסדר (0,1,2...) |
| **אחסון** | PVC חיצוני | PVC אוטומטי לכל pod |
| **Network** | Service רגיל | Headless + Regular Service |
| **High Availability** | לא | כן (replica set) |
| **Data Persistence** | בסיסי | מתקדם |
| **Scaling** | מוגבל | יעיל |
| **Recovery** | איטי | מהיר |

---

## 🛠️ הוראות פריסה

### 1. Deployment (גישה רגילה)

```bash
# הגדרת משתנים
export APP_NAME="soldiers-api"
export DATABASE_NAME="enemy_soldiers"
export COLLECTION_NAME="soldier_details"
export MONGO_VERSION="8.0"
export STORAGE_SIZE="2Gi"
export STORAGE_CLASS="gp2"
export MONGO_ROOT_PASSWORD="jhsdyttfe65fds54scf65"

# משאבים
export MONGO_CPU_REQUEST="200m"
export MONGO_MEMORY_REQUEST="256Mi" 
export MONGO_CPU_LIMIT="500m"
export MONGO_MEMORY_LIMIT="512Mi"
export CONFIG_CHECKSUM="$(date +%s)"

# פריסה
envsubst < kubernetes-templates/databases/mongodb/deployment-complete.yaml | oc apply -f -

# בדיקה
oc wait --for=condition=ready pod -l app.kubernetes.io/instance=${APP_NAME}-mongo --timeout=300s
oc logs -l app.kubernetes.io/instance=${APP_NAME}-mongo
```

### 2. StatefulSet (גישה מתקדמת)

```bash
# הגדרת משתנים בסיסיים (כמו למעלה) + 
export MONGO_REPLICAS="3"
export NAMESPACE="$(oc project -q)"
export MONGO_REPLICA_SET_KEY="your-secret-replica-key-min-1024-chars"

# יצירת replica set key חזק
export MONGO_REPLICA_SET_KEY="$(openssl rand -base64 756)"

# פריסה
envsubst < kubernetes-templates/databases/mongodb/statefulset-complete.yaml | oc apply -f -

# בדיקת פריסה מדורגת
for i in {0..2}; do
  echo "Waiting for ${APP_NAME}-mongo-statefulset-$i..."
  oc wait --for=condition=ready pod ${APP_NAME}-mongo-statefulset-$i --timeout=300s
done

# בדיקת replica set
oc exec ${APP_NAME}-mongo-statefulset-0 -- mongosh --eval "rs.status()"
```

---

## 🔧 פקודות תחזוקה

### Deployment Commands

```bash
# בדיקת סטטוס
oc get deployment,pvc,svc -l app.kubernetes.io/instance=${APP_NAME}-mongo

# גיבוי נתונים
oc exec -it deployment/${APP_NAME}-mongo-deployment -- mongodump --archive > backup.archive

# שחזור נתונים
oc exec -i deployment/${APP_NAME}-mongo-deployment -- mongorestore --archive < backup.archive

# סקיילינג (לא מומלץ למונגו)
oc scale deployment ${APP_NAME}-mongo-deployment --replicas=0
oc scale deployment ${APP_NAME}-mongo-deployment --replicas=1

# מחיקה
oc delete deployment,pvc,svc,configmap,secret -l app.kubernetes.io/instance=${APP_NAME}-mongo
```

### StatefulSet Commands

```bash
# בדיקת סטטוס מתקדם
oc get statefulset,pvc,svc -l app.kubernetes.io/instance=${APP_NAME}-mongo

# בדיקת replica set
oc exec ${APP_NAME}-mongo-statefulset-0 -- mongosh --eval "
  rs.status().members.forEach(function(member) {
    print(member.name + ' - ' + member.stateStr);
  });
"

# הוספת replica (scaling up)
oc patch statefulset ${APP_NAME}-mongo-statefulset -p '{"spec":{"replicas":4}}'

# גיבוי מרפליקה ספציפית
oc exec -it ${APP_NAME}-mongo-statefulset-1 -- mongodump --archive > backup-replica1.archive

# rolling restart
oc rollout restart statefulset/${APP_NAME}-mongo-statefulset

# מחיקה מדורגת
oc delete statefulset ${APP_NAME}-mongo-statefulset
oc delete pvc -l app.kubernetes.io/instance=${APP_NAME}-mongo
oc delete svc,configmap,secret,networkpolicy,pdb -l app.kubernetes.io/instance=${APP_NAME}-mongo
```

---

## 🔒 אבטחה והרשאות

### Security Context
- **runAsUser: 999** (MongoDB user)
- **runAsNonRoot: true** 
- **fsGroup: 999** (file permissions)

### Network Policies
- **Deployment**: מאפשר חיבור רק מ-API pods
- **StatefulSet**: מאפשר גם חיבור בין replica members

### RBAC (StatefulSet)
- **ServiceAccount**: לzoo discovery
- **Role**: גישה לpods API
- **RoleBinding**: חיבור בין SA לRole

---

## 🚨 פתרון בעיות נפוצות

### Deployment Issues

**Pod לא עולה:**
```bash
# בדוק events
oc describe pod -l app.kubernetes.io/instance=${APP_NAME}-mongo

# בדוק PVC
oc describe pvc ${APP_NAME}-mongo-pvc

# בדוק storage class
oc get storageclass
```

**אין חיבור למסד:**
```bash
# בדוק שהservice זמין
oc get svc ${APP_NAME}-mongo-service

# בדוק connectivity
oc run test-pod --image=busybox --rm -it -- nslookup ${APP_NAME}-mongo-service
```

### StatefulSet Issues

**Replica Set לא מאותחל:**
```bash
# בדוק logs של pod 0
oc logs ${APP_NAME}-mongo-statefulset-0

# אתחל ידני
oc exec ${APP_NAME}-mongo-statefulset-0 -- mongosh --eval "
  rs.initiate({
    _id: '${APP_NAME}-rs',
    members: [
      {_id: 0, host: '${APP_NAME}-mongo-statefulset-0.${APP_NAME}-mongo-headless-service:27017'}
    ]
  });
"
```

**Pod תקוע ב-Pending:**
```bash
# בדוק PVC status
oc get pvc | grep ${APP_NAME}-mongo

# בדוק node resources
oc describe nodes

# בדוק pod anti-affinity
oc describe pod ${APP_NAME}-mongo-statefulset-1
```

---

## ⚡ טיפים למטובי ביצועים

### משאבים מומלצים

**Development:**
```bash
MONGO_CPU_REQUEST="100m"
MONGO_MEMORY_REQUEST="128Mi"
MONGO_CPU_LIMIT="200m"
MONGO_MEMORY_LIMIT="256Mi"
STORAGE_SIZE="1Gi"
```

**Production:**
```bash
MONGO_CPU_REQUEST="500m"
MONGO_MEMORY_REQUEST="1Gi"
MONGO_CPU_LIMIT="2"
MONGO_MEMORY_LIMIT="4Gi"
STORAGE_SIZE="20Gi"
```

### Storage Classes מומלצות

**AWS:** `gp3`, `io1`
**GCP:** `ssd`, `pd-ssd`
**Azure:** `managed-premium`
**OpenShift:** `ocs-storagecluster-ceph-rbd`

### מומלץ לפרודקשן

1. **השתמש ב-StatefulSet** עם לפחות 3 replicas
2. **הגדר Pod Disruption Budget** 
3. **השתמש ב-NetworkPolicy** לאבטחה
4. **נטר משאבים** עם Prometheus
5. **בצע גיבויים קבועים**
6. **בדוק replica set health** באופן קבוע

---

## 📊 מוניטורינג ומדדים

### בדיקות בריאות בסיסיות

```bash
# בדיקת חיבור
oc exec ${APP_NAME}-mongo-statefulset-0 -- mongosh --eval "db.adminCommand('ping')"

# בדיקת replica set
oc exec ${APP_NAME}-mongo-statefulset-0 -- mongosh --eval "rs.status()"

# בדיקת משתמשים
oc exec ${APP_NAME}-mongo-statefulset-0 -- mongosh --eval "db.adminCommand('listUsers')"

# בדיקת collections
oc exec ${APP_NAME}-mongo-statefulset-0 -- mongosh ${DATABASE_NAME} --eval "show collections"
```

### מדדי ביצועים

```bash
# בדיקת אחסון
oc exec ${APP_NAME}-mongo-statefulset-0 -- mongosh ${DATABASE_NAME} --eval "db.stats()"

# בדיקת indexes
oc exec ${APP_NAME}-mongo-statefulset-0 -- mongosh ${DATABASE_NAME} --eval "db.${COLLECTION_NAME}.getIndexes()"

# בדיקת connections
oc exec ${APP_NAME}-mongo-statefulset-0 -- mongosh --eval "db.serverStatus().connections"
```