<script setup>
import { defineProps, ref, onMounted, onBeforeUnmount } from "vue";

import { removeTask } from "./stores/tasks";
import { formatSecondsToHMS } from "./util";

const props = defineProps(["task", "duration-modal"]);

import { ClockIcon, TrashIcon } from "@heroicons/vue/16/solid";
import { apiFetch } from "./api";

const runningTaskId = ref(null);
const estDuration = ref(0);
const elapsedTime = ref(0);
let interval = null;

const gettingDeleted = ref(false);

const checkRunningInstance = async () => {
    try {
        const data = await apiFetch(`/tasks/${props.task.id}/instances/elapsed`);
        runningTaskId.value = props.task.id;
        estDuration.value = data.est_duration_sec;
        elapsedTime.value = data.elapsed_sec;
        startTimer(props.task.id);
    } catch (err) {
        // No running instance
        runningTaskId.value = null;
    }
};

const startNewInstance = async (task) => {
    const estTime = await props.durationModal.show(
        "Enter duration",
        "01:30:00",
    );
    if (!isNaN(estTime) && estTime > 0) {
        try {
            await apiFetch(`/tasks/${task.id}/instances/start`, {
                method: "POST",
                body: JSON.stringify({ est_duration_sec: estTime }),
            });
            runningTaskId.value = task.id;
            estDuration.value = estTime;
            elapsedTime.value = 0;
            startTimer(task.id);
        } catch (err) {
            console.error("Failed to start instance:", err);
        }
    }
};

const stopInstance = async (task) => {
    try {
        await apiFetch(`/tasks/${task.id}/instances/stop`, {
            method: "POST",
        });
        clearInterval(interval);
        runningTaskId.value = null;
        estDuration.value = 0;
        elapsedTime.value = 0;
        // Reload tasks to update the UI
        const { loadTasks } = await import("./stores/tasks");
        await loadTasks();
    } catch (err) {
        console.error("Failed to stop instance:", err);
    }
};

const startTimer = (taskId) => {
    if (interval) clearInterval(interval);
    interval = setInterval(async () => {
        try {
            const data = await apiFetch(`/tasks/${taskId}/instances/elapsed`);
            elapsedTime.value = data.elapsed_sec;
        } catch (err) {
            console.error("Failed to get elapsed time:", err);
            clearInterval(interval);
        }
    }, 1000);
};

onMounted(() => {
    checkRunningInstance();
});

onBeforeUnmount(() => {
    if (interval) clearInterval(interval);
});
</script>

<template>
    <div :class="{ card: true, disabled: gettingDeleted }">
        <h2 class="flex">
            <RouterLink :to="`/task/${task.id}`"
                >{{ task.icon }} {{ task.title }}</RouterLink
            >
            <button
                class="inline danger"
                style="font-size: 14px"
                :disabled="gettingDeleted"
                @click="
                    () => {
                        removeTask(task.id);
                        gettingDeleted = true;
                    }
                "
            >
                <TrashIcon class="inline-icon" />
            </button>
        </h2>

        <template v-if="runningTaskId === task.id">
            <ClockIcon class="inline-icon" /> Running... Estimated:
            {{ formatSecondsToHMS(estDuration) }}
            Elapsed: {{ formatSecondsToHMS(elapsedTime) }}<br />
            <button class="danger full-width" @click="stopInstance(task)">
                Complete Task
            </button>
        </template>
        <template v-else>
            Avg. estimate: {{ formatSecondsToHMS(task.getAvgEstTime()) }}<br />
            Avg. actual: {{ formatSecondsToHMS(task.getAvgRealTime()) }}<br />
            Avg. bias: {{ formatSecondsToHMS(task.getAvgTimeBias()) }} ({{
                task.getAvgTimeBiasPercentage()?.toFixed(1)
            }}%)<br />
            <button
                :disabled="gettingDeleted"
                class="full-width"
                @click="startNewInstance(task)"
            >
                Start Tracking
            </button>
        </template>
    </div>
</template>

<style scoped>
div.card {
    background-color: var(--bg-alt);
    border-radius: 8px;
    padding: 15px;
    margin: 15px 0px;
    transition: opacity 0.3s ease-in-out;
}

div.card * {
    transition: opacity 0.3s ease-in-out;
}

div.card.disabled {
    opacity: 0.5;
}
</style>