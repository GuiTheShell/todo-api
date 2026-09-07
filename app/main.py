from flask import Flask, jsonify, request
from app.models import db, Task
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

VALID_PRIORITIES = ["baixa", "média", "alta"]


@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "API de Lista de Tarefas rodando com sucesso!"})


@app.route("/tasks", methods=["GET"])
def list_tasks():
    completed_param = request.args.get("completed")

    if completed_param is not None:
        completed_bool = completed_param.lower() == "true"
        tasks = Task.query.filter_by(completed=completed_bool).all()
    else:
        tasks = Task.query.all()

    return jsonify([task.to_dict() for task in tasks])


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict())


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()

    if not data or not data.get("title"):
        return jsonify({"error": "O campo 'title' é obrigatório"}), 400

    priority = data.get("priority", "média")

    if priority not in VALID_PRIORITIES:
        return jsonify({
            "error": "O campo 'priority' deve ser: baixa, média ou alta"
        }), 400

    task = Task(
        title=data["title"],
        description=data.get("description", ""),
        completed=False,
        priority=priority,
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()

    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.completed = data.get("completed", task.completed)

    if "priority" in data:
        if data["priority"] not in VALID_PRIORITIES:
            return jsonify({
                "error": "O campo 'priority' deve ser: baixa, média ou alta"
            }), 400

        task.priority = data["priority"]


    db.session.commit()
    return jsonify(task.to_dict())


@app.route("/tasks/<int:task_id>/complete", methods=["PATCH"])
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = True
    db.session.commit()
    return jsonify(task.to_dict())


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Tarefa removida com sucesso",
                    
                    })


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
