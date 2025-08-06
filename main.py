import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
import os
import re

# Banco de dados
conn = sqlite3.connect('despesas.db')
cursor = conn.cursor()

# Criação das tabelas
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS despesas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    categoria TEXT NOT NULL,
    data TEXT NOT NULL,
    valor TEXT NOT NULL,
    descricao TEXT,
    FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
)
''')
conn.commit()

# Inserir usuário padrão
try:
    cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", ("admin", "admin"))
    conn.commit()
except sqlite3.IntegrityError:
    pass  # Usuário já existe

usuario_id_logado = None

def login():
    global usuario_id_logado
    user = entry_usuario.get()
    pwd = entry_senha.get()

    cursor.execute("SELECT id FROM usuarios WHERE usuario=? AND senha=?", (user, pwd))
    result = cursor.fetchone()

    if result:
        usuario_id_logado = result[0]
        login_frame.pack_forget()
        mostrar_janela_principal()
    else:
        messagebox.showerror("Erro", "Usuário ou senha inválidos")

def logout():
    global usuario_id_logado
    usuario_id_logado = None
    main_frame.pack_forget()
    login_frame.pack(padx=20, pady=20)

def adicionar_despesa():
    categoria = combo_categoria.get()
    data = entry_data.get()
    valor = entry_valor.get()
    descricao = entry_descricao.get()

    if not categoria or not data or not valor:
        messagebox.showwarning("Aviso", "Preencha todos os campos obrigatórios.")
        return

    cursor.execute("INSERT INTO despesas (usuario_id, categoria, data, valor, descricao) VALUES (?, ?, ?, ?, ?)",
                   (usuario_id_logado, categoria, data, valor, descricao))
    conn.commit()
    atualizar_lista()
    limpar_campos()

def excluir_despesa():
    selected = tree.focus()
    if not selected:
        return

    id_despesa = tree.item(selected)['values'][0]
    cursor.execute("DELETE FROM despesas WHERE id=? AND usuario_id=?", (id_despesa, usuario_id_logado))
    conn.commit()
    atualizar_lista()

def exportar_csv():
    filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if not filepath:
        return

    cursor.execute("SELECT categoria, data, valor, descricao FROM despesas WHERE usuario_id=?", (usuario_id_logado,))
    dados = cursor.fetchall()

    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Categoria", "Data", "Valor", "Descrição"])
        writer.writerows(dados)

    messagebox.showinfo("Exportado", "Despesas exportadas com sucesso!")

def atualizar_lista():
    for i in tree.get_children():
        tree.delete(i)

    cursor.execute("SELECT id, categoria, data, valor, descricao FROM despesas WHERE usuario_id=?", (usuario_id_logado,))
    total = 0
    for row in cursor.fetchall():
        tree.insert('', 'end', values=row)
        valor_str = row[3].replace("R$", "").replace(".", "").replace(",", ".")
        try:
            total += float(valor_str)
        except:
            pass

    label_total.config(text=f"Total: R$ {total:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ','))

def limpar_campos():
    combo_categoria.set('')
    entry_data.delete(0, tk.END)
    entry_valor.delete(0, tk.END)
    entry_descricao.delete(0, tk.END)

def formatar_data(event):
    texto = entry_data.get()
    texto = re.sub(r'\D', '', texto)
    if len(texto) >= 2:
        texto = texto[:2] + '/' + texto[2:]
    if len(texto) >= 5:
        texto = texto[:5] + '/' + texto[5:]
    entry_data.delete(0, tk.END)
    entry_data.insert(0, texto[:10])

def formatar_valor(event):
    texto = re.sub(r'\D', '', entry_valor.get())
    if texto:
        valor = int(texto)
        valor_formatado = f"R$ {valor / 100:,.2f}".replace(".", "X").replace(",", ".").replace("X", ",")
        entry_valor.delete(0, tk.END)
        entry_valor.insert(0, valor_formatado)

# Interface
root = tk.Tk()
root.title("Gerenciador de Despesas")
root.geometry("700x500")
root.configure(bg="#f0f0f0")

# LOGIN
login_frame = tk.Frame(root, bg="#f0f0f0")
tk.Label(login_frame, text="Usuário:", bg="#f0f0f0").pack()
entry_usuario = tk.Entry(login_frame)
entry_usuario.pack()
tk.Label(login_frame, text="Senha:", bg="#f0f0f0").pack()
entry_senha = tk.Entry(login_frame, show="*")
entry_senha.pack()
tk.Button(login_frame, text="Entrar", command=login).pack(pady=10)
login_frame.pack(padx=20, pady=20)

# PRINCIPAL
main_frame = tk.Frame(root, bg="#f0f0f0")

frame_form = tk.Frame(main_frame, bg="#f0f0f0")
frame_form.pack(pady=10)

tk.Label(frame_form, text="Categoria:", bg="#f0f0f0").grid(row=0, column=0)
combo_categoria = ttk.Combobox(frame_form, values=["Alimentação", "Transporte", "Lazer", "Saúde", "Outros"], width=15)
combo_categoria.grid(row=0, column=1)

tk.Label(frame_form, text="Data (DD/MM/AAAA):", bg="#f0f0f0").grid(row=1, column=0)
entry_data = tk.Entry(frame_form)
entry_data.grid(row=1, column=1)
entry_data.bind('<KeyRelease>', formatar_data)

tk.Label(frame_form, text="Valor (R$):", bg="#f0f0f0").grid(row=2, column=0)
entry_valor = tk.Entry(frame_form)
entry_valor.grid(row=2, column=1)
entry_valor.bind('<KeyRelease>', formatar_valor)

tk.Label(frame_form, text="Descrição:", bg="#f0f0f0").grid(row=3, column=0)
entry_descricao = tk.Entry(frame_form, width=30)
entry_descricao.grid(row=3, column=1)

tk.Button(main_frame, text="Adicionar Despesa", command=adicionar_despesa, bg="#4caf50", fg="white").pack(pady=5)
tk.Button(main_frame, text="Excluir Despesa", command=excluir_despesa, bg="#f44336", fg="white").pack(pady=5)
tk.Button(main_frame, text="Exportar CSV", command=exportar_csv, bg="#2196f3", fg="white").pack(pady=5)
tk.Button(main_frame, text="Logout", command=logout, bg="#9e9e9e", fg="white").pack(pady=5)

tree = ttk.Treeview(main_frame, columns=("ID", "Categoria", "Data", "Valor", "Descrição"), show='headings', height=10)
tree.pack(pady=10)

for col in tree["columns"]:
    tree.heading(col, text=col)
    tree.column(col, width=100)

label_total = tk.Label(main_frame, text="Total: R$ 0,00", font=("Arial", 12, "bold"), bg="#f0f0f0")
label_total.pack(pady=5)

def mostrar_janela_principal():
    main_frame.pack(padx=20, pady=20)
    atualizar_lista()

root.mainloop()
